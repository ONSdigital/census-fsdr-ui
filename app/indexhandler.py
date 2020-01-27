import aiohttp_jinja2
import math

from aiohttp.client_exceptions import (ClientResponseError)
from aiohttp.web import HTTPFound, RouteTableDef
from aiohttp_session import get_session
from app.searchfunctions import get_distinct_job_role, get_employee_records, \
    get_employee_count
from structlog import get_logger

from . import (NEED_TO_SIGN_IN_MSG, NO_EMPLOYEE_DATA, SERVICE_DOWN_MSG)
from .flash import flash

logger = get_logger('fsdr-ui')
index_route = RouteTableDef()
employee_count_base_url = "http://localhost:5678/fieldforce/employeeCount/"


def setup_request(request):
    request['client_ip'] = request.headers.get('X-Forwarded-For', None)


def log_entry(request, endpoint):
    method = request.method
    logger.info(f"received {method} on endpoint '{endpoint}'",
                method=request.method,
                path=request.path)


@index_route.view('/index+{page}')
class MainPage:
    @aiohttp_jinja2.template('index.html')
    async def get(self, request):
        session = await get_session(request)
        page_number = int(request.match_info['page'])

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
                employee_count = get_employee_count(request)
                max_page = int(employee_count.text) / 50
                if page_number >= max_page:
                    page_number = int(math.floor(max_page))
                else:
                    if page_number > 1:
                        low_value = 50 * page_number
                        high_value = low_value + 50
                    else:
                        low_value = page_number
                        high_value = 50
                    get_employee_info = get_employee_records(request, low_value, high_value)
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

            if get_employee_info.status_code == 200:
                employee_records_json = get_employee_info.json()
                job_role_json = get_job_roles.json()
                return {
                    'page_title': f'Field Force view for: {user_role}',
                    'employee_records': employee_records_json,
                    'page_number': page_number,
                    'last_page_number': int(math.floor(max_page)),
                    'distinct_job_roles': job_role_json
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
