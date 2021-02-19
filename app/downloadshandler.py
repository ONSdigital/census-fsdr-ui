import json
import math
import uuid
import glob

import aiohttp_jinja2

from aiohttp.client_exceptions import (ClientResponseError)
from aiohttp.web import HTTPFound, RouteTableDef
from aiohttp_session import get_session
from structlog import get_logger
from app.pageutils import page_bounds
from app.role_matchers import has_download_permission
from app.error_handlers import client_response_error, warn_invalid_login

from app.searchfunctions import (get_all_assignment_status,
                                 get_microservice_records,
                                 iat_employee_record_table,
                                 iat_employee_table_headers,
                                 get_distinct_job_role_short,
                                 get_employee_count)

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

    if has_download_permission(user_role):
      pass
    else:
      return aiohttp_jinja2.render_template('error404.html', request,
                                            {'include_nav': True})

    try:
      search_range, records_per_page = page_bounds(1)

      search_range = {'rangeHigh': 10, 'rangeLow': 0}
      get_employee_info = get_microservice_records("iattable",
                                                   user_filter=search_range)
      get_employee_info_json = get_employee_info.json()

      if len(get_employee_info_json) > 0:
        employee_sum = get_employee_info_json[0].get('total_records', 0)

        # If there are more than 0 people in iat
        # then get_employee_info is set to everyone (max is total number of employees)
        search_range = {'rangeHigh': employee_sum, 'rangeLow': 0}
        get_employee_info = get_microservice_records("iattable", search_range)
        get_employee_info_json = get_employee_info.json()

        html_employee_records = iat_employee_record_table(
            get_employee_info_json, remove_html=True)
        html_headers = iat_employee_table_headers()

    except ClientResponseError as ex:
      client_response_error(ex, request)

    if get_employee_info.status_code == 200:

      headers = ""
      for html_header in html_headers:
        headers = headers + str(html_header.get('value')) + " , "
      headers = headers[:-3]

      rows = ""
      for employee_record in html_employee_records:
        rows = str(rows) + "\n"
        for each_array in employee_record.get('tds'):
          rows = str(rows) + str(each_array.get('value')) + " , "
        rows = rows[:-3]

      if download_type == "iat":
        path = "/opt/ui/app/assets/iat/"

        # Delete all files in /opt/ui/app/assets/iat
        files = glob.glob(path + '*')
        for f in files:
          os.remove(f)

        # Create unique file name
        file_name = f'{uuid.uuid4()}.csv'

        with open(path + file_name, "w+") as of:
          of.write(str(headers))
          of.write(str(rows))

        download_location = "/assets/iat/" + file_name
      else:
        logger.warn(f"Unknown download type: {download_type}")

      return {
          'download_location': download_location,
      }
    else:
      logger.warn('Database is down', client_ip=request['client_ip'])
      flash(request, NO_EMPLOYEE_DATA)
      raise HTTPFound(request.app.router['MainPage:get'].url_for())
