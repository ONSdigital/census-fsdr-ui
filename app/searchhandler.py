import math
import re

import aiohttp_jinja2

from aiohttp.client_exceptions import (ClientResponseError)
from aiohttp.web import HTTPFound, RouteTableDef
from aiohttp_session import get_session
from structlog import get_logger

from app.searchfunctions import get_all_assignment_status, get_distinct_job_role, get_employee_records, \
    get_employee_count
from . import (NEED_TO_SIGN_IN_MSG, NO_EMPLOYEE_DATA, SERVICE_DOWN_MSG)
from .flash import flash
from flask import Flask

logger = get_logger('fsdr-ui')
search_routes = RouteTableDef()
employee_count_base_url = "http://localhost:5678/fieldforce/employeeCount/"
app = Flask(__name__)


def setup_request(request):
    request['client_ip'] = request.headers.get('X-Forwarded-For', None)


def log_entry(request, endpoint):
    method = request.method
    logger.info(f"received {method} on endpoint '{endpoint}'",
                method=request.method,
                path=request.path)


@search_routes.view('/search')
class Search:
    @aiohttp_jinja2.template('search.html')
    async def get(self, request):
        session = await get_session(request)
        try:
            user_json = session['user_details']
            user_role = user_json['userRole']
        except ClientResponseError:
            flash(request, NEED_TO_SIGN_IN_MSG)
            raise HTTPFound(
                request.app.router['Login:get'].url_for())

        if session.get('logged_in'):
            setup_request(request)
            log_entry(request, 'start')

            try:
                get_job_roles = get_distinct_job_role(request)
                get_all_assignment_statuses = get_all_assignment_status(request)
            except ClientResponseError as ex:
                if ex.status == 503:
                    logger.warn('Server is unavailable',
                                client_ip=request['client_ip'])
                    flash(request, SERVICE_DOWN_MSG)
                    raise HTTPFound(
                        request.app.router.url_for('error503.html')
                    )
                else:
                    raise ex

            if get_job_roles.status_code == 200 and get_all_assignment_statuses.status_code == 200:
                job_role_json = get_job_roles.json()
                assignment_statuses_json = get_all_assignment_statuses.json()
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
                    request.app.router['MainPage:get'].url_for(page=0))

        else:
            flash(request, NEED_TO_SIGN_IN_MSG)
            raise HTTPFound(
                request.app.router['Login:get'].url_for())


@search_routes.view('/search+{page}+{called_from_index}+{previous_query}+{retrieve_count}')
class SecondaryPage:
    @aiohttp_jinja2.template('search-results.html')
    async def post(self, request):
        session = await get_session(request)
        page_number = int(request.match_info['page'])
        data = await request.post()
        from_index = request.match_info['called_from_index']

        try:
            user_json = session['user_details']
            user_role = user_json['userRole']
        except ClientResponseError:
            flash(request, NEED_TO_SIGN_IN_MSG)
            raise HTTPFound(
                request.app.router['Login:get'].url_for())

        if session.get('logged_in'):
            setup_request(request)
            log_entry(request, 'start')

            previous_assignment_selected = ''
            previous_jobrole_selected = ''
            previous_area = ''
            previous_surname = ''
            previous_firstname = ''
            previous_badge = ''
            previous_jobid = ''

            try:
                user_filter = ''
                format_user_filter = ''

                if data.get('assignment_select'):
                    previous_assignment_selected = data.get('assignment_select')
                    selected_assignment = '&assignmentStatus=' + previous_assignment_selected
                    if user_filter == '':
                        user_filter = selected_assignment
                        format_user_filter = '?assignmentStatus=' + previous_assignment_selected
                    else:
                        user_filter = user_filter + '&' + selected_assignment
                        format_user_filter = format_user_filter + '&assignmentStatus=' + previous_assignment_selected

                if data.get('job_role_select'):
                    previous_jobrole_selected = data.get('job_role_select')
                    selected_job_role = '&jobRole=' + previous_jobrole_selected
                    if user_filter == '':
                        user_filter = selected_job_role
                        format_user_filter = '?jobRole=' + previous_jobrole_selected
                    else:
                        user_filter = user_filter + '&' + selected_job_role
                        format_user_filter = format_user_filter + '&jobRole=' + previous_jobrole_selected

                if data.get('filter_area'):
                    previous_area = data.get('filter_area')
                    filter_area = '&area=' + previous_area
                    if user_filter == '':
                        user_filter = filter_area
                        format_user_filter = '?area=' + previous_area
                    else:
                        user_filter = user_filter + filter_area
                        format_user_filter = format_user_filter + '&area=' + previous_area

                if data.get('filter_surname'):
                    previous_surname = data.get('filter_surname')
                    filter_surname = '&surname=' + previous_surname
                    if user_filter == '':
                        user_filter = filter_surname
                        format_user_filter = '?surname=' + previous_surname
                    else:
                        user_filter = user_filter + filter_surname
                        format_user_filter = format_user_filter + '&surname=' + previous_surname

                if data.get('filter_firstname'):
                    previous_firstname = data.get('filter_firstname')
                    filter_firstname = '&firstName=' + previous_firstname
                    if user_filter == '':
                        user_filter = filter_firstname
                        format_user_filter = '?firstName=' + previous_firstname
                    else:
                        user_filter = user_filter + filter_firstname
                        format_user_filter = format_user_filter + '&firstNme=' + previous_firstname

                if data.get('filter_badge'):
                    previous_badge = data.get('filter_badge')
                    filter_badge = '&badgeNumber=' + previous_badge
                    if user_filter == '':
                        user_filter = filter_badge
                        format_user_filter = '?badgeNumber=' + previous_badge
                    else:
                        user_filter = user_filter + filter_badge
                        format_user_filter = format_user_filter + '&badgeNumber=' + previous_badge

                if data.get('filter_jobid'):
                    previous_jobid = data.get('filter_jobid')
                    filter_jobid = '&jobRoleId=' + previous_jobid
                    if user_filter == '':
                        user_filter = filter_jobid
                        format_user_filter = '?jobRoleId=' + previous_jobid
                    else:
                        user_filter = user_filter + filter_jobid
                        format_user_filter = format_user_filter + '&jobRoleId=' + previous_jobid

                if user_filter == '' and from_index == 'true':
                    raise HTTPFound(
                        request.app.router['MainPage:get'].url_for(page='1'))
                elif user_filter == '' and from_index == 'false':
                    return aiohttp_jinja2.render_template(
                        'search.html',
                        request, {
                            'no_search_criteria': 'True'
                        },
                        status=405)

                high_value, low_value, page_number, max_page = await self.allocate_search_ranges(request,
                                                                                                 format_user_filter,
                                                                                                 page_number)

                retrieve_employee_info = get_employee_records(request, low_value,
                                                              high_value, user_filter)

                get_job_roles = get_distinct_job_role(request)

            except ClientResponseError as ex:
                    raise ex

            if retrieve_employee_info.status_code == 200:
                employee_records_json = retrieve_employee_info.json()
                job_role_json = get_job_roles.json()
                return {
                    'called_from_index': from_index,
                    'page_title': f'Field Force view for: {user_role}',
                    'employee_records': employee_records_json,
                    'page_number': page_number,
                    'last_page_number': int(math.floor(max_page)),
                    'distinct_job_roles': job_role_json,
                    'previous_selection': user_filter,
                    'previous_area': previous_area,
                    'previous_assignment_selected': previous_assignment_selected,
                    'previous_jobrole_selected': previous_jobrole_selected,
                    'previous_firstname': previous_firstname,
                    'previous_badge': previous_badge,
                    'previous_jobid': previous_jobid,
                    'previous_surname_filter': previous_surname,
                }
            else:
                logger.warn('Attempted to login with invalid user name and/or password',
                            client_ip=request['client_ip'])
                flash(request, NO_EMPLOYEE_DATA)
                return aiohttp_jinja2.render_template(
                    'signin.html',
                    request, {
                        'display_region': 'en',
                        'page_title': 'Sign in'
                    },
                    status=401)

        else:
            flash(request, NEED_TO_SIGN_IN_MSG)
            raise HTTPFound(
                request.app.router['Login:get'].url_for())

    @aiohttp_jinja2.template('search-results.html')
    async def get(self, request):
        session = await get_session(request)
        page_number = int(request.match_info['page'])
        previous_query = request.match_info['previous_query']
        from_index = request.match_info['called_from_index']

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

            try:
                if previous_query == "default":
                    user_filter = ""
                    format_user_filter = ""
                else:
                    user_filter = previous_query
                    format_user_filter = previous_query.replace("&", "?", 1)

                high_value, low_value, page_number, max_page = await self.allocate_search_ranges(request,
                                                                                                 format_user_filter,
                                                                                                 page_number)

                retrieve_employee_info = get_employee_records(request, low_value,
                                                              high_value, user_filter)
                get_job_roles = get_distinct_job_role(request)
            except ClientResponseError as ex:
                if ex.status == 503:
                    logger.warn('Server is unavailable',
                                client_ip=request['client_ip'])
                    flash(request, SERVICE_DOWN_MSG)
                    raise HTTPFound(
                        request.app.router.url_for('error503.html')
                    )
                else:
                    raise ex

            except ClientResponseError as ex:
                    raise ex

            if retrieve_employee_info.status_code == 200:
                previous_assignment_selected = ''
                previous_jobrole_selected = ''
                previous_area = ''
                previous_surname = ''
                previous_firstname = ''
                previous_badge = ''
                previous_jobid = ''
                employee_records_json = retrieve_employee_info.json()
                job_role_json = get_job_roles.json()

                split_user_filter = user_filter.replace("&", "", 1)
                filter_form_list = re.split('&|=', split_user_filter)

                filter_form_dict = {filter_form_list[i]: filter_form_list[i + 1]
                                    for i in range(0, len(filter_form_list), 2)}

                if 'area' in filter_form_dict.keys():
                    previous_area = filter_form_dict['area']

                if 'jobRole' in filter_form_dict.keys():
                    previous_jobrole_selected = filter_form_dict['jobRole']

                if 'surname' in filter_form_dict.keys():
                    previous_surname = filter_form_dict['surname']

                if 'assignmentStatus' in filter_form_dict.keys():
                    previous_assignment_selected = filter_form_dict['assignmentStatus']

                if 'jobRoleId' in filter_form_dict.keys():
                    previous_jobid = filter_form_dict['jobRoleId']

                if 'firstName' in filter_form_dict.keys():
                    previous_surname = filter_form_dict['firstName']

                if 'badgeNumber' in filter_form_dict.keys():
                    previous_surname = filter_form_dict['badgeNumber']

                return {
                    'called_from_index': from_index,
                    'page_title': f'Field Force view for: {user_role}',
                    'employee_records': employee_records_json,
                    'page_number': int(page_number),
                    'last_page_number': int(math.floor(max_page)),
                    'distinct_job_roles': job_role_json,
                    'previous_selection': user_filter,
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
                        'display_region': 'en',
                        'page_title': 'Sign in'
                    },
                    status=401)

        else:
            flash(request, NEED_TO_SIGN_IN_MSG)
            raise HTTPFound(
                request.app.router['Login:get'].url_for())

    async def allocate_search_ranges(self, request, user_filter, page_number):
        employee_count = get_employee_count(request, user_filter)

        max_page = int(employee_count.text) / 50
        if page_number >= max_page:
            page_number = int(math.floor(max_page))
        if page_number == 0:
            low_value = 1
            high_value = 50
        elif page_number > 1:
            low_value = 50 * page_number
            high_value = low_value + 50
        else:
            low_value = page_number
            high_value = 50
        return high_value, low_value, page_number, max_page
