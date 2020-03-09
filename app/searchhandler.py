import json
import math

import aiohttp_jinja2

from aiohttp.client_exceptions import (ClientResponseError)
from aiohttp.web import HTTPFound, RouteTableDef
from aiohttp_session import get_session
from structlog import get_logger

from app.searchcriteria import store_search_criteria, retrieve_job_roles, retrieve_assignment_statuses, \
    clear_stored_search_criteria
from app.searchfunctions import get_all_assignment_status, get_distinct_job_role, get_employee_records, \
    allocate_search_ranges, employee_record_table, employee_table_headers
from . import (NEED_TO_SIGN_IN_MSG, NO_EMPLOYEE_DATA, SERVICE_DOWN_MSG)
from .flash import flash
from flask import Flask

logger = get_logger('fsdr-ui')
search_routes = RouteTableDef()
app = Flask(__name__)


@search_routes.view('/search')
class Search:
    @aiohttp_jinja2.template('search.html')
    async def get(self, request):
        session = await get_session(request)

        if session.get('logged_in'):
            await clear_stored_search_criteria(session)
            user_json = session['user_details']
            user_role = user_json['userRole']

            try:
                get_job_roles = get_distinct_job_role()
                get_all_assignment_statuses = get_all_assignment_status()
            except ClientResponseError as ex:
                if ex.status == 503:
                    logger.warn('Server is unavailable',
                                client_ip=request['client_ip'])
                    flash(request, SERVICE_DOWN_MSG)
                    return aiohttp_jinja2.render_template(
                        'error503.html',
                        request, {
                            'include_nav': False
                        })
                else:
                    raise ex

            if get_job_roles.status_code == 200 and get_all_assignment_statuses.status_code == 200:

                job_role_json = retrieve_job_roles(get_job_roles, '')
                assignment_statuses_json = retrieve_assignment_statuses(get_all_assignment_statuses)

                return {
                    'page_title': f'Field Force view for: {user_role}',
                    'distinct_job_roles': job_role_json,
                    'all_assignment_statuses': assignment_statuses_json
                }
            else:
                logger.warn('Database is down',
                            client_ip=request['client_ip'])
                flash(request, NO_EMPLOYEE_DATA)
                raise HTTPFound(
                    request.app.router['MainPage:get'].url_for())

        else:
            flash(request, NEED_TO_SIGN_IN_MSG)
            return aiohttp_jinja2.render_template(
                'signin.html',
                request, {
                    'include_nav': False
                })


@search_routes.view('/search-results')
class SecondaryPage:
    @aiohttp_jinja2.template('search-results.html')
    async def post(self, request):
        session = await get_session(request)
        data = await request.post()

        try:
            user_json = session['user_details']
            user_role = user_json['userRole']
        except ClientResponseError:
            flash(request, NEED_TO_SIGN_IN_MSG)
            return aiohttp_jinja2.render_template(
                'signin.html',
                request, {
                    'include_nav': False
                })

        if session.get('logged_in'):

            if 'page' in request.query:
                page_number = int(request.query['page'])
            else:
                page_number = 1

            previous_assignment_selected = ''
            previous_jobrole_selected = ''
            previous_area = ''
            previous_surname = ''
            previous_firstname = ''
            previous_badge = ''
            previous_jobid = ''

            try:
                if data.get('indexsearch') == '' or 'called_from_index' in request.query:
                    from_index = 'true'
                else:
                    from_index = 'false'

                search_criteria = {}

                if data.get('assignment_select'):
                    previous_assignment_selected = data.get('assignment_select')
                    search_criteria['assignmentStatus'] = previous_assignment_selected

                if data.get('job_role_select'):
                    previous_jobrole_selected = data.get('job_role_select')
                    search_criteria['jobRole'] = previous_jobrole_selected

                if data.get('filter_area'):
                    previous_area = data.get('filter_area')
                    search_criteria['area'] = previous_area

                if data.get('filter_surname'):
                    previous_surname = data.get('filter_surname')
                    search_criteria['surname'] = previous_surname

                if data.get('filter_firstname'):
                    previous_firstname = data.get('filter_firstname')
                    search_criteria['firstName'] = previous_firstname

                if data.get('filter_badge'):
                    previous_badge = data.get('filter_badge')
                    search_criteria['badgeNumber'] = previous_badge

                if data.get('filter_jobid'):
                    previous_jobid = data.get('filter_jobid')
                    search_criteria['jobRoleId'] = previous_jobid

                if search_criteria:
                    await store_search_criteria(request, search_criteria)

                if search_criteria == '' and from_index == 'true':
                    raise HTTPFound(
                        request.app.router['MainPage:get'].url_for())
                elif search_criteria == '' and from_index == 'false':
                    return aiohttp_jinja2.render_template(
                        'search.html',
                        request, {
                            'no_search_criteria': 'True'
                        },
                        status=405)

                high_value, low_value, page_number, max_page = await allocate_search_ranges(search_criteria,
                                                                                            page_number)

                search_criteria_with_range = search_criteria.copy()

                search_criteria_with_range['rangeHigh'] = high_value
                search_criteria_with_range['rangeLow'] = low_value

                retrieve_employee_info = get_employee_records(search_criteria_with_range)

                get_job_roles = get_distinct_job_role()

            except ClientResponseError as ex:
                raise ex

            if retrieve_employee_info.status_code == 200:
                table_headers = employee_table_headers()

                employees_present = retrieve_employee_info.content
                if employees_present == b'[]':
                    no_employee_data = 'true'
                else:
                    no_employee_data = 'false'
                    employee_records = employee_record_table(retrieve_employee_info.json())

                job_role_json = retrieve_job_roles(get_job_roles, previous_jobrole_selected)

                return {
                    'called_from_index': from_index,
                    'page_title': f'Field Force view for: {user_role}',
                    'table_headers': table_headers,
                    'employee_records': employee_records,
                    'page_number': page_number,
                    'last_page_number': int(math.floor(max_page)),
                    'distinct_job_roles': job_role_json,
                    'previous_selection': json.dumps(search_criteria),
                    'previous_area': previous_area,
                    'previous_assignment_selected': previous_assignment_selected,
                    'previous_jobrole_selected': previous_jobrole_selected,
                    'previous_firstname': previous_firstname,
                    'previous_badge': previous_badge,
                    'previous_jobid': previous_jobid,
                    'previous_surname_filter': previous_surname,
                    'no_employee_data': no_employee_data
                }
            else:
                logger.warn('Attempted to login with invalid user name and/or password',
                            client_ip=request['client_ip'])
                flash(request, NO_EMPLOYEE_DATA)
                return aiohttp_jinja2.render_template(
                    'signin.html',
                    request, {
                        'page_title': 'Sign in',
                        'include_nav': False
                    },
                    status=401)

        else:
            flash(request, NEED_TO_SIGN_IN_MSG)
            return aiohttp_jinja2.render_template(
                'signin.html',
                request, {
                    'page_title': 'Sign in',
                    'include_nav': False
                })

    @aiohttp_jinja2.template('search-results.html')
    async def get(self, request):
        session = await get_session(request)

        try:
            user_json = session['user_details']
            user_role = user_json['userRole']
        except:
            flash(request, NEED_TO_SIGN_IN_MSG)
            raise HTTPFound(
                request.app.router['Login:get'].url_for())

        if session.get('logged_in'):
            setup_request(request)
            log_entry(request, 'start')

            if 'page' in request.query:
                page_number = int(request.query['page'])
            else:
                page_number = 1

            if 'called_from_index' in request.query:
                from_index = request.query['called_from_index']
            else:
                from_index = False

            search_criteria = {}

            previous_assignment_selected = ''
            previous_jobrole_selected = ''
            previous_area = ''
            previous_surname = ''
            previous_firstname = ''
            previous_badge = ''
            previous_jobid = ''
            try:
                if session.get('assignmentStatus'):
                    previous_assignment_selected = session['assignmentStatus']
                    search_criteria['assignmentStatus'] = previous_assignment_selected

                if session.get('jobRole'):
                    previous_jobrole_selected = session['jobRole']
                    search_criteria['jobRole'] = previous_jobrole_selected

                if session.get('area'):
                    previous_area = session['area']
                    search_criteria['area'] = previous_area

                if session.get('surname'):
                    previous_surname = session['surname']
                    search_criteria['surname'] = previous_surname

                if session.get('firstName'):
                    previous_firstname = session['firstName']
                    search_criteria['firstName'] = previous_firstname

                if session.get('badgeNumber'):
                    previous_badge = session['badgeNumber']
                    search_criteria['badgeNumber'] = previous_badge

                if session.get('jobRoleId'):
                    previous_jobid = session['jobRoleId']
                    search_criteria['jobRoleId'] = previous_jobid

                high_value, low_value, page_number, max_page = await allocate_search_ranges(search_criteria,
                                                                                            page_number)

                search_criteria_with_range = search_criteria.copy()

                search_criteria_with_range['rangeHigh'] = high_value
                search_criteria_with_range['rangeLow'] = low_value

                retrieve_employee_info = get_employee_records(search_criteria_with_range)

                get_job_roles = get_distinct_job_role()
            except ClientResponseError as ex:
                if ex.status == 503:
                    logger.warn('Server is unavailable',
                                client_ip=request['client_ip'])
                    flash(request, SERVICE_DOWN_MSG)
                    return aiohttp_jinja2.render_template(
                        'error503.html',
                        request, {
                            'include_nav': False
                        })
                else:
                    raise ex

            except ClientResponseError as ex:
                raise ex

            if retrieve_employee_info.status_code == 200:
                table_headers = employee_table_headers()

                employee_records = employee_record_table(retrieve_employee_info.json())

                job_role_json = retrieve_job_roles(get_job_roles, previous_jobrole_selected)

                return {
                    'called_from_index': from_index,
                    'page_title': f'Field Force view for: {user_role}',
                    'table_headers': table_headers,
                    'employee_records': employee_records,
                    'page_number': int(page_number),
                    'last_page_number': int(math.floor(max_page)),
                    'distinct_job_roles': job_role_json,
                    'previous_selection': json.dumps(search_criteria),
                    'previous_area': previous_area,
                    'previous_assignment_selected': previous_assignment_selected,
                    'previous_jobrole_selected': previous_jobrole_selected,
                    'previous_firstname': previous_firstname,
                    'previous_badge': previous_badge,
                    'previous_jobid': previous_jobid,
                    'previous_surname_filter': previous_surname
                }
            else:
                logger.warn('Attempted to login with invalid user name and/or password',
                            client_ip=request['client_ip'])
                flash(request, NO_EMPLOYEE_DATA)
                return aiohttp_jinja2.render_template(
                    'signin.html',
                    request, {
                        'page_title': 'Sign in',
                        'include_nav': False
                    })

        else:
            flash(request, NEED_TO_SIGN_IN_MSG)
            return aiohttp_jinja2.render_template(
                'signin.html',
                request, {
                    'page_title': 'Sign in',
                    'include_nav': False
                })
