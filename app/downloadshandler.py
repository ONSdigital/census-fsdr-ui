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

import csv
import json

logger = get_logger('fsdr-ui')
downloads_routes = RouteTableDef()

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

STATIC_DIR = os.path.abspath('../static')


def setup_request(request):
    request['client_ip'] = request.headers.get('X-Forwarded-For', None)


def log_entry(request, endpoint):
    method = request.method
    logger.info(f"received {method} on endpoint '{endpoint}'",
                method=request.method,
                path=request.path)


@downloads_routes.view('/downloads/{download_type}')
class DownloadsPage:
    @aiohttp_jinja2.template('downloads.html')
    async def get(self, request):
        download_type = request.match_info['download_type']
        session = await get_session(request)
        await saml.ensure_logged_in(request)

        user_role = await saml.get_role_id(request)

        try:
            search_range, records_per_page = page_bounds(1)

            get_employee_info = get_employee_records(search_range, iat = True)
            get_employee_info_json = get_employee_info.json() 

            if len(get_employee_info_json) > 0: 
                employee_sum = get_employee_info_json[0].get('total_employees',0) 

                # If there are more than 0 people in iat
                # then get_employee_info is set to everyone (max is total number of employees)
                search_range = {'rangeHigh': employee_sum, 'rangeLow': 0}
                get_employee_info = get_employee_records(search_range, iat = True)
                get_employee_info_json = get_employee_info.json() 

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

            headers = iat_employee_table_headers()
            employee_records = iat_employee_record_table(get_employee_info_json)
             
            logger.error("employee  records:\n" + str(employee_records))

            download_location = "./README.md"
            return {
                'download_location': download_location,
            }
        else:
            logger.warn('Database is down', client_ip=request['client_ip'])
            flash(request, NO_EMPLOYEE_DATA)
            raise HTTPFound(request.app.router['MainPage:get'].url_for())
