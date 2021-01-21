import json
import math

import aiohttp_jinja2

from aiohttp.client_exceptions import (ClientResponseError)
from aiohttp.web import HTTPFound, RouteTableDef
from aiohttp_session import get_session
from structlog import get_logger
from app.pageutils import page_bounds

from app.searchcriteria import (
    store_search_criteria,
    retrieve_job_roles,
    retrieve_assignment_statuses,
    clear_stored_search_criteria,
    retreive_iat_statuses
)

from app.searchfunctions import (
    get_all_assignment_status,
    get_employee_records, 
    allocate_search_ranges,
    iat_employee_record_table,
    iat_employee_table_headers,
    get_distinct_job_role_short,
    get_employee_count
)

from . import (NEED_TO_SIGN_IN_MSG, NO_EMPLOYEE_DATA, SERVICE_DOWN_MSG)
from . import saml
from .flash import flash

import sys
import os


logger = get_logger('fsdr-ui')
interface_action_handler_table_routes = RouteTableDef()


def setup_request(request):
    request['client_ip'] = request.headers.get('X-Forwarded-For', None)


def log_entry(request, endpoint):
    method = request.method
    logger.info(f"received {method} on endpoint '{endpoint}'",
                method=request.method,
                path=request.path)


@interface_action_handler_table_routes.view('/interfaceactiontable')
class InterfaceActionTable:
    @aiohttp_jinja2.template('interfaceactiontable.html')
    async def get(self, request):
        session = await get_session(request)

        await saml.ensure_logged_in(request)

        await clear_stored_search_criteria(session)
        setup_request(request)
        log_entry(request, 'start')

        user_role = await saml.get_role_id(request)

        if 'page' in request.query:
            page_number = int(request.query['page'])
        else:
            page_number = 1

        try:
            search_range, records_per_page = page_bounds(page_number)

            get_employee_info = get_employee_records(search_range, iat = True).json()

            if len(get_employee_info) > 0:
                employee_sum = get_employee_info[0].get('total_employees',0)
                max_page = ceil((employee_sum / records_per_page) - 1)
            else:
                max_page = 1 

            get_job_roles = get_distinct_job_role_short()

        except ClientResponseError as ex:
            if ex.status == 503:
                ip = request['client_ip']
                logger.warn('Server is unavailable', client_ip=ip)
                flash(request, SERVICE_DOWN_MSG)
                return aiohttp_jinja2.render_template('error503.html', request,
                                                      {'include_nav': False})
            else:
                raise ex

        if get_employee_info.status_code == 200:
            table_headers = iat_employee_table_headers()

            employee_records = iat_employee_record_table(get_employee_info)

            job_role_json = retrieve_job_roles(get_job_roles, '')
            
            iat_stats = retreive_iat_statuses()    
            return {
                'page_title': f'Interface Action Table view for: {user_role}',
                'table_headers': table_headers,
                'employee_records': employee_records,
                'page_number': page_number,
                'last_page_number': int(math.floor(max_page)),
                'distinct_job_roles': job_role_json,
                'iat_options': iat_stats,
            }
        else:
            logger.warn('Database is down', client_ip=request['client_ip'])
            flash(request, NO_EMPLOYEE_DATA)
            raise HTTPFound(request.app.router['MainPage:get'].url_for())


#  Below is  from  search handler and  allows the  iat  to do  similar  funcionatlity, but in addiotn will search IAT

@interface_action_handler_table_routes.view('/iat-search-results')
class IatSecondaryPage:
    @aiohttp_jinja2.template('iat-search-results.html')
    async def post(self, request):
        session = await get_session(request)
        data = await request.post()

        user_role = await saml.get_role_id(request)

        await saml.ensure_logged_in(request)

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
            if data.get('indexsearch'
                        ) == '' or 'called_from_index' in request.query:
                from_index = 'true'
            else:
                from_index = 'false'

            search_criteria = {}

            if data.get('assignment_select'):
                previous_assignment_selected = data.get('assignment_select')
                search_criteria['assignmentStatus'] = data.get(
                    'assignment_select')

            if data.get('job_role_select'):
                previous_jobrole_selected = data.get('job_role_select')
                search_criteria['jobRoleShort'] = data.get('job_role_select')

            select_options = ["gsuite_select","xma_select","granby_select","loneWorker_select","serviceNow_select"]
            for select_element in select_options:
                if data.get(select_element):
                    if data.get(select_element)  != "blank":
                        search_criteria[str(select_element.split("_")[0])] = data.get(select_element)

            if data.get('filter_unique_employee_id'):
                unique_employee_id = data.get('filter_unique_employee_id')
                search_criteria['uniqueEmployeeId'] = unique_employee_id

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

            if data.get('filter_email'):
                previous_email = data.get('filter_email')
                search_criteria['email'] = previous_email

            if search_criteria:
                await store_search_criteria(request, search_criteria)

            if search_criteria == '' and from_index == 'true':
                raise HTTPFound(request.app.router['InterfaceActionTable:get'].url_for())
            elif search_criteria == '' and from_index == 'false':
                return aiohttp_jinja2.render_template(
                    'search.html',
                    request, {'no_search_criteria': 'True'},
                    status=405)

            last_record, first_record, page_number, max_page = await allocate_search_ranges(
                search_criteria, page_number)

            search_criteria_with_range = search_criteria.copy()

            search_criteria_with_range['rangeHigh'] = last_record 
            search_criteria_with_range['rangeLow'] =  first_record 

            retrieve_employee_info = get_employee_records(
                search_criteria_with_range, iat = True)

            get_job_roles = get_distinct_job_role_short()

        except ClientResponseError as ex:
            raise ex

        if retrieve_employee_info.status_code == 200:
            table_headers = iat_employee_table_headers()

            employees_present = retrieve_employee_info.content
            if employees_present == b'[]':
                no_employee_data = 'true'
                employee_records = ''
            else:
                no_employee_data = 'false'
                employee_records = iat_employee_record_table(
                    retrieve_employee_info.json())

            job_role_short_json = retrieve_job_roles(
                get_job_roles, previous_jobrole_selected)

            iat_stats = retreive_iat_statuses()    
            return {
                'called_from_index': from_index,
                'page_title': f'Interface Action Table view for: {user_role}',
                'table_headers': table_headers,
                'employee_records': employee_records,
                'page_number': page_number,
                'last_page_number': int(math.floor(max_page)),
                'distinct_job_roles': job_role_short_json,
                'previous_selection': json.dumps(search_criteria),
                'previous_area': previous_area,
                'previous_assignment_selected': previous_assignment_selected,
                'previous_jobrole_selected': previous_jobrole_selected,
                'previous_firstname': previous_firstname,
                'previous_badge': previous_badge,
                'previous_jobid': previous_jobid,
                'previous_surname_filter': previous_surname,
                'no_employee_data': no_employee_data,
                'iat_options': iat_stats,
            }
        else:
            logger.warn(
                'Attempted to login with invalid user name and/or password',
                client_ip=request['client_ip'])
            flash(request, NO_EMPLOYEE_DATA)
            return aiohttp_jinja2.render_template('signin.html',
                                                  request, {
                                                      'page_title': 'Sign in',
                                                      'include_nav': False
                                                  },
                                                  status=401)

    @aiohttp_jinja2.template('iat-search-results.html')
    async def get(self, request):
        session = await get_session(request)

        user_role = await saml.get_role_id(request)

        await saml.ensure_logged_in(request)

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
                search_criteria[
                    'assignmentStatus'] = previous_assignment_selected

            if session.get('jobRoleShort'):
                previous_jobrole_selected = session['jobRoleShort']
                search_criteria['jobRoleShort'] = previous_jobrole_selected

        #Changed to allow ID filtering

            if session.get('filter_unique_employee_id'):
                unique_employee_id = data.get('filter_unique_employee_id')
                search_criteria['uniqueEmployeeId'] = unique_employee_id

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

            last_record, first_record, page_number, max_page = await allocate_search_ranges(
                search_criteria, page_number)

            search_criteria_with_range = search_criteria.copy()

            search_criteria_with_range['rangeHigh'] = last_record 
            search_criteria_with_range['rangeLow'] =  first_record 

            retrieve_employee_info = get_employee_records(
                search_criteria_with_range, iat = True)

            get_job_roles = get_distinct_job_role_short()
        except ClientResponseError as ex:
            if ex.status == 503:
                logger.warn('Server is unavailable',
                            client_ip=request['client_ip'])
                flash(request, SERVICE_DOWN_MSG)
                return aiohttp_jinja2.render_template('error503.html', request,
                                                      {'include_nav': False})
            else:
                raise ex

        except ClientResponseError as ex:
            raise ex

        if retrieve_employee_info.status_code == 200:
            table_headers = iat_employee_table_headers()

            employee_records = iat_employee_record_table(
                retrieve_employee_info.json())

            job_role_json = retrieve_job_roles(get_job_roles,
                                               previous_jobrole_selected)
            iat_stats = retreive_iat_statuses()    
            return {
                'called_from_index': from_index,
                'page_title': f'Interface Action Table view for: {user_role}',
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
                'previous_surname_filter': previous_surname,
                'iat_options':iat_stats, 
            }
        else:
            logger.warn(
                'Attempted to login with invalid user name and/or password',
                client_ip=request['client_ip'])
            flash(request, NO_EMPLOYEE_DATA)
            return aiohttp_jinja2.render_template('signin.html', request, {
                'page_title': 'Sign in',
                'include_nav': False
            })

