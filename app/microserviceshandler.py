import json
import math

import aiohttp_jinja2

from aiohttp.client_exceptions import (ClientResponseError)
from aiohttp.web import HTTPFound, RouteTableDef
from aiohttp_session import get_session
from structlog import get_logger
from app.pageutils import page_bounds, get_page
from app.error_handlers import client_response_error, warn_invalid_login
from app.role_matchers import  download_permission
from app.microservice_tables import (
    get_table_headers,
    get_table_records,
    get_fields,
    get_fields_to_load,
)

from app.searchcriteria import (
    store_search_criteria,
    load_search_criteria,
    clear_stored_search_criteria,
)

from app.searchfunctions import (
    allocate_search_ranges,
    get_microservice_records,
)

from . import (NEED_TO_SIGN_IN_MSG, NO_EMPLOYEE_DATA, SERVICE_DOWN_MSG)
from . import saml
from .flash import flash

import sys
import os


logger = get_logger('fsdr-ui')
microservices_handler_routes = RouteTableDef()

def setup_request(request):
    request['client_ip'] = request.headers.get('X-Forwarded-For', None)


def log_entry(request, endpoint):
    method = request.method
    logger.info(f"received {method} on endpoint '{endpoint}'",
                method=request.method,
                path=request.path)

@microservices_handler_routes.view('/microservices/{microservice_name}')
class MicroservicesTable:
    @aiohttp_jinja2.template('microservices.html')
    async def post(self, request):
        session = await get_session(request)
        data = await request.post()

        user_role = await saml.get_role_id(request)

        await saml.ensure_logged_in(request)

        microservice_title = request.match_info['microservice_name'].replace("table"," Table").title()
        microservice_name = request.match_info['microservice_name']
        page_number = get_page(request)

        try:

            Fields = get_fields(microservice_name) 
            table_headers = get_table_headers(Fields) # formatted for table use
            fields_to_load = get_fields_to_load(Fields)

            search_criteria, previous_criteria = load_search_criteria(data, fields_to_load)

            if search_criteria:
                await store_search_criteria(request, search_criteria)

            if search_criteria == '' and from_index == 'true':
                raise HTTPFound(request.app.router['MicroservicesTable:get'].url_for())
            elif search_criteria == '' and from_index == 'false':
                return aiohttp_jinja2.render_template(
                    'search.html',
                    request, {'no_search_criteria': 'True'},
                    status=405)

            search_range, records_per_page = page_bounds(page_number)
            search_criteria.update(search_range)

            get_microservice_info = get_microservice_records(microservice_name, 
                                                             user_filter=search_criteria)
            get_microservice_info_json = get_microservice_info.json() 
            
            if len(get_microservice_info_json) > 0:
                microservice_sum = get_microservice_info_json[0].get('total_devices',0)
                max_page = math.ceil(microservice_sum / records_per_page)        
            else:
                max_page = 1 

        except ClientResponseError as ex:
            client_response_error(ex, request)

        if get_microservice_info.status_code == 200:
            # for 0 response st no_records true

            table_records = get_table_records(Fields, get_microservice_info_json)   # database name field ([gsuite_status,...
            
            return {
                'called_from_index': False,
                'Fields':Fields,
                'microservice_name': microservice_name,
                'microservice_title': microservice_title, 
                'page_title': f'{microservice_title} view for: {user_role}',
                'dst_download': download_permission(user_role),
                'page_number': page_number,
                'last_page_number': 0,
                'table_headers': table_headers,
                'table_records': table_records,
                }
            return warn_invalid_login(request)


    @aiohttp_jinja2.template('microservices.html')
    async def get(self, request):
        session = await get_session(request)

        user_role = await saml.get_role_id(request)

        await saml.ensure_logged_in(request)

        microservice_title = request.match_info['microservice_name'].replace("table"," Table").title()
        microservice_name = request.match_info['microservice_name']
        page_number = get_page(request)

        try:
            Fields = get_fields(microservice_name) 
            table_headers = get_table_headers(Fields) # formatted for table use
            fields_to_load = get_fields_to_load(Fields)

            search_criteria, previous_criteria = load_search_criteria(session, fields_to_load)

            search_range, records_per_page = page_bounds(page_number)
            search_criteria.update(search_range)

            get_microservice_info = get_microservice_records(microservice_name,user_filter=search_criteria)
            get_microservice_info_json = get_microservice_info.json() 
            
            if len(get_microservice_info_json) > 0:
                device_sum = get_microservice_info_json[0].get('total_devices',0)
                max_page = math.ceil(device_sum / records_per_page)        
            else:
                max_page = 1 

        except ClientResponseError as ex:
            client_response_error(ex, request)

        if get_microservice_info.status_code == 200:
            table_records = get_table_records(Fields, get_microservice_info_json)   # database name field ([gsuite_status,...
            return {
                'called_from_index': False,
                'Fields':Fields,
                'microservice_name':microservice_name,
                'microservice_title': microservice_title,
                'page_title': f'{microservice_title} view for: {user_role}',
                'dst_download': download_permission(user_role),
                'page_number': page_number,
                'last_page_number': 0,
                'table_headers': table_headers,
                'table_records': table_records,
                }
        else:
            return warn_invalid_login(request)
