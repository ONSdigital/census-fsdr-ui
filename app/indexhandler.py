import os
import sys

import aiohttp_jinja2
import math

from aiohttp.client_exceptions import (ClientResponseError)
from aiohttp.web import HTTPFound, RouteTableDef
from aiohttp_session import get_session

from app.searchcriteria import retrieve_job_roles, clear_stored_search_criteria
from app.pageutils import page_bounds

from app.searchfunctions import (
        get_employee_records, 
        get_employee_count,
        employee_record_table,
        employee_table_headers,
        get_distinct_job_role_short
)

from structlog import get_logger

from . import (NEED_TO_SIGN_IN_MSG, NO_EMPLOYEE_DATA, SERVICE_DOWN_MSG)
from . import saml
from .flash import flash

logger = get_logger('fsdr-ui')
index_route = RouteTableDef()

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

STATIC_DIR = os.path.abspath('../static')


def setup_request(request):
    request['client_ip'] = request.headers.get('X-Forwarded-For', None)


def log_entry(request, endpoint):
    method = request.method
    logger.info(f"received {method} on endpoint '{endpoint}'",
                method=request.method,
                path=request.path)


@index_route.view('/index')
class MainPage:
    @aiohttp_jinja2.template('index.html')
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
            table_headers = employee_table_headers()

            employee_records = employee_record_table(get_employee_info.json())

            job_role_json = retrieve_job_roles(get_job_roles, '')

            return {
                'page_title': f'Field Force view for: {user_role}',
                'table_headers': table_headers,
                'employee_records': employee_records,
                'page_number': page_number,
                'last_page_number': int(math.floor(max_page)),
                'distinct_job_roles': job_role_json,
            }
        else:
            logger.warn('Database is down', client_ip=request['client_ip'])
            flash(request, NO_EMPLOYEE_DATA)
            raise HTTPFound(request.app.router['MainPage:get'].url_for())
