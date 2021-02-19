import os
import sys

import aiohttp_jinja2
import math

from aiohttp.client_exceptions import (ClientResponseError)
from aiohttp.web import HTTPFound, RouteTableDef
from aiohttp_session import get_session

from app.searchcriteria import retrieve_job_roles, clear_stored_search_criteria
from app.pageutils import page_bounds, get_page, result_message
from app.error_handlers import client_response_error, warn_invalid_login
from app.role_matchers import has_download_permission

from app.searchfunctions import (get_employee_records, get_employee_count,
                                 employee_record_table, employee_table_headers,
                                 get_distinct_job_role_short)

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

    page_number = get_page(request)

    try:
      search_range, records_per_page = page_bounds(page_number)

      get_employee_info = get_employee_records(search_range)
      get_employee_info_json = get_employee_info.json()

      if len(get_employee_info_json) > 0:
        employee_sum = get_employee_info_json[0].get('total_employees', 0)
        max_page = math.ceil(employee_sum / records_per_page)
      else:
        employee_sum = 0
        max_page = 1

      get_job_roles = get_distinct_job_role_short()

    except ClientResponseError as ex:
      client_response_error(ex, request)

    if get_employee_info.status_code == 200:
      table_headers = employee_table_headers()

      employee_records = employee_record_table(get_employee_info_json)

      job_role_json = retrieve_job_roles(get_job_roles, '')

      result_message_str = result_message(search_range, employee_sum,
                                          "Employee Table")
      return {
          'result_message': result_message_str,
          'page_title': f'Field Force view for: {user_role}',
          'table_headers': table_headers,
          'employee_records': employee_records,
          'page_number': page_number,
          'last_page_number': int(math.floor(max_page)),
          'distinct_job_roles': job_role_json,
          'dst_download': has_download_permission(user_role),
      }
    else:
      logger.warn('Database is down', client_ip=request['client_ip'])
      flash(request, NO_EMPLOYEE_DATA)
      raise HTTPFound(request.app.router['MainPage:get'].url_for())
