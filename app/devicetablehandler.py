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
    retreive_iat_statuses,
    device_type_dropdown,
    device_sent_dropdown,
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

        try:
            search_range, records_per_page = page_bounds(page_number)

            get_device_info = get_device_records(search_range, iat=True)
            get_device_info_json = get_device_info.json() 

            if len(get_device_info_json) > 0:
                device_sum = get_device_info_json[0].get('total_devices',0)
                    
                search_range = {'rangeHigh': last_record, 'rangeLow': first_record}
                get_device_info =  get_device_records(search_range, iat=True) 

        except ClientResponseError as ex:
            if ex.status == 503:
                ip = request['client_ip']
                logger.warn('Server is unavailable', client_ip=ip)
                flash(request, SERVICE_DOWN_MSG)
                return aiohttp_jinja2.render_template('error503.html', request,
                                                      {'include_nav': False})
            else:
                raise ex

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
            }
        else:
            logger.warn('Database is down', client_ip=request['client_ip'])
            flash(request, NO_EMPLOYEE_DATA)
            raise HTTPFound(request.app.router['MainPage:get'].url_for())

