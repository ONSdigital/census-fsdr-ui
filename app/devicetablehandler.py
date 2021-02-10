import json
import math

import aiohttp_jinja2

from aiohttp.client_exceptions import (ClientResponseError)
from aiohttp.web import HTTPFound, RouteTableDef
from aiohttp_session import get_session
from structlog import get_logger
from app.pageutils import page_bounds, get_page
from app.error_handlers import client_response_error, warn_invalid_login
from app.role_matchers import download_permission

from app.searchcriteria import (
    store_search_criteria,
    load_search_criteria,
    retrieve_job_roles,
    retrieve_assignment_statuses,
    clear_stored_search_criteria,
    retreive_iat_statuses,
    device_type_dropdown,
    device_sent_dropdown,
)

from app.searchfunctions import (
    get_all_assignment_status,
    get_device_records, 
    allocate_search_ranges,
    device_records_table,
    device_table_headers,
    get_distinct_job_role_short,
    get_employee_count
)

from . import (NEED_TO_SIGN_IN_MSG, NO_EMPLOYEE_DATA, SERVICE_DOWN_MSG)
from . import saml
from .flash import flash

import sys
import os


logger = get_logger('fsdr-ui')
device_table_handler_routes = RouteTableDef()


def setup_request(request):
    request['client_ip'] = request.headers.get('X-Forwarded-For', None)


def log_entry(request, endpoint):
    method = request.method
    logger.info(f"received {method} on endpoint '{endpoint}'",
                method=request.method,
                path=request.path)


@device_table_handler_routes.view('/devicetable')
class DeviceTable:
    @aiohttp_jinja2.template('devicetable.html')
    async def get(self, request):
        session = await get_session(request)

        await saml.ensure_logged_in(request)

        await clear_stored_search_criteria(session)
        setup_request(request)
        log_entry(request, 'start')

        user_role = await saml.get_role_id(request)

        page_number = get_page(request)

        try:
            search_range, records_per_page = page_bounds(page_number)

            get_device_info = get_device_records(search_range)
            get_device_info_json = get_device_info.json() 

            if len(get_device_info_json) > 0:
                device_sum = get_device_info_json[0].get('total_devices',0)
                max_page = math.ceil(device_sum / records_per_page)        
            else:
                max_page = 1 

        except ClientResponseError as ex:
            client_response_error(ex, request)

        if get_device_info.status_code == 200:
            table_headers = device_table_headers()

            device_records = device_records_table(get_device_info_json)
            device_type_dropdown_options = device_type_dropdown('blank')
            device_sent_dropdown_options = device_sent_dropdown('blank')

            return {
                'page_title': f'Device Table view for: {user_role}',
                'table_headers': table_headers,
                'device_records': device_records,
                'page_number': page_number,
                'last_page_number': max_page,
                'device_type_options': device_type_dropdown_options,
                'device_sent_options': device_sent_dropdown_options,
                'dst_download': download_permission(user_role),
            }
        else:
            logger.warn('Database is down', client_ip=request['client_ip'])
            flash(request, NO_EMPLOYEE_DATA)
            raise HTTPFound(request.app.router['MainPage:get'].url_for())


@device_table_handler_routes.view('/device-search-results')
class DeviceSecondaryPage:
    @aiohttp_jinja2.template('device-search-results.html')
    async def post(self, request):
        session = await get_session(request)
        data = await request.post()

        user_role = await saml.get_role_id(request)

        await saml.ensure_logged_in(request)

        page_number = get_page(request)

        try:
            if data.get('indexsearch'
                        ) == '' or 'called_from_index' in request.query:
                from_index = 'true'
            else:
                from_index = 'false'

            fields_to_load = ["device_sent","device_id","field_device_phone_number",
                    "device_type","ons_id"]

            search_criteria, previous_criteria = load_search_criteria(data, fields_to_load)

            if search_criteria:
                await store_search_criteria(request, search_criteria)

            if search_criteria == '' and from_index == 'true':
                raise HTTPFound(request.app.router['DeviceTable:get'].url_for())
            elif search_criteria == '' and from_index == 'false':
                return aiohttp_jinja2.render_template(
                    'search.html',
                    request, {'no_search_criteria': 'True'},
                    status=405)


            search_range, records_per_page = page_bounds(page_number)
            search_criteria.update(search_range)

            get_device_info = get_device_records(search_criteria)
            get_device_info_json = get_device_info.json() 
            
            if len(get_device_info_json) > 0:
                device_sum = get_device_info_json[0].get('total_devices',0)
                max_page = math.ceil(device_sum / records_per_page)        
            else:
                max_page = 1 

        except ClientResponseError as ex:
            return client_response_error(ex, request)

        if get_device_info.status_code == 200:
            table_headers = device_table_headers()

            devices_present = get_device_info.content
            if devices_present == b'[]':
                no_device_data = 'true'
                device_records = ''
            else:
                no_device_data  = 'false'
                device_records  = device_records_table(
                        get_device_info_json)

            device_type_dropdown_options = device_type_dropdown(previous_criteria.get('device_type'))
            device_sent_dropdown_options = device_sent_dropdown(previous_criteria.get('device_sent'))

            return {
                'called_from_index': from_index,
                'device_sent_options': device_sent_dropdown_options,
                'device_type_options': device_type_dropdown_options,
                'previous_device_id': previous_criteria.get('device_id'),
                'previous_field_device_phone_number': previous_criteria.get('field_device_phone_number'),
                'previous_ons_id': previous_criteria.get('ons_id'),
                'page_title': f'Device Table view for: {user_role}',
                'table_headers': table_headers,
                'device_records': device_records,
                'page_number': page_number,
                'last_page_number': int(math.floor(max_page)),
                'dst_download': download_permission(user_role),
            }
        else:
            return warn_invalid_login(request)

    @aiohttp_jinja2.template('device-search-results.html')
    async def get(self, request):
        session = await get_session(request)

        user_role = await saml.get_role_id(request)

        await saml.ensure_logged_in(request)

        page_number = get_page(request)

        if 'called_from_index' in request.query:
            from_index = request.query['called_from_index']
        else:
            from_index = False

        try:

            fields_to_load = ["device_sent","device_id","field_device_phone_number",
                    "device_type","ons_id"]

            search_criteria, previous_criteria = load_search_criteria(session, fields_to_load)

            search_range, records_per_page = page_bounds(page_number)
            search_criteria.update(search_range)

            get_device_info = get_device_records(search_criteria)
            get_device_info_json = get_device_info.json() 
            
            if len(get_device_info_json) > 0:
                device_sum = get_device_info_json[0].get('total_devices',0)
                max_page = math.ceil(device_sum / records_per_page)        
            else:
                max_page = 1 

        except ClientResponseError as ex:
            return client_response_error(ex, request)

        if get_device_info.status_code == 200:
            table_headers = device_table_headers()

            device_records = device_records_table(
                get_device_info_json)

            device_type_dropdown_options = device_type_dropdown(previous_criteria.get('device_type'))
            device_sent_dropdown_options = device_sent_dropdown(previous_criteria.get('device_sent'))

            return {
                'called_from_index': from_index,
                'page_title': f'Device Table view for: {user_role}',
                'device_sent_options': device_sent_dropdown_options,
                'device_type_options': device_type_dropdown_options,
                'previous_device_id': previous_criteria.get('device_id'),
                'previous_field_device_phone_number': previous_criteria.get('field_device_phone_number'),
                'previous_ons_id': previous_criteria.get('ons_id'),
                'table_headers': table_headers,
                'device_records': device_records,
                'page_number': int(page_number),
                'last_page_number': int(math.floor(max_page)),
                'dst_download': download_permission(user_role),
            }
        else:
            return warn_invalid_login(request)
