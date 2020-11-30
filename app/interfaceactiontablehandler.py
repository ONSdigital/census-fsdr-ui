import os
import sys

import aiohttp_jinja2
import math

from aiohttp.client_exceptions import (ClientResponseError)
from aiohttp.web import HTTPFound, RouteTableDef
from aiohttp_session import get_session

from app.searchcriteria import retrieve_job_roles, clear_stored_search_criteria
from app.searchfunctions import get_employee_records, \
    get_employee_count, iat_employee_record_table, iat_employee_table_headers, get_distinct_job_role_short
from structlog import get_logger

from . import (NEED_TO_SIGN_IN_MSG, NO_EMPLOYEE_DATA, SERVICE_DOWN_MSG)
from . import saml
from .flash import flash

logger = get_logger('fsdr-ui')
interface_action_handler_table_routes = RouteTableDef()

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

STATIC_DIR = os.path.abspath('../static')


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
            employee_count = get_employee_count()
            max_page = (int(employee_count.text) / 50) - 1
            if page_number >= max_page > 1:
                page_number = int(math.floor(max_page))
            else:
                if max_page < 1:
                    max_page = 1
                if page_number > 1:
                    low_value = 50 * page_number
                    high_value = low_value + 50
                else:
                    low_value = page_number
                    high_value = 50

                search_range = {'rangeHigh': high_value, 'rangeLow': low_value}

                get_employee_info = get_employee_records(search_range)
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

            employee_records = iat_employee_record_table(get_employee_info.json())

            job_role_json = retrieve_job_roles(get_job_roles, '')

            return {
                'page_title': f'Field Force view for: {user_role}',
                'table_headers': iat_table_headers,
                'employee_records': employee_records,
                'page_number': page_number,
                'last_page_number': int(math.floor(max_page)),
                'distinct_job_roles': job_role_json,
            }
        else:
            logger.warn('Database is down', client_ip=request['client_ip'])
            flash(request, NO_EMPLOYEE_DATA)
            raise HTTPFound(request.app.router['MainPage:get'].url_for())
