import json
import math
import uuid

import aiohttp_jinja2

from aiohttp.client_exceptions import (ClientResponseError)
from aiohttp.web import HTTPFound, RouteTableDef
from aiohttp_session import get_session
from structlog import get_logger
from app.microservice_tables import get_table_records, get_table_headers
from app.role_matchers import has_download_permission
from app.error_handlers import client_response_error, warn_invalid_login
from app.pageutils import page_bounds

from app.microservice_tables import (
    get_table_headers,
    get_table_records,
    get_fields,
)
from app.searchfunctions import (
    get_all_assignment_status,
    get_microservice_records,
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


def setup_request(request):
  request['client_ip'] = request.headers.get('X-Forwarded-For', None)


def log_entry(request, endpoint):
  method = request.method
  logger.info(f"received {method} on endpoint '{endpoint}'",
              method=request.method,
              path=request.path)


@downloads_routes.view('/downloads/{microservice_name}')
class DownloadsPage:
  @aiohttp_jinja2.template('downloads.html')
  async def get(self, request):
    microservice_name = request.match_info['microservice_name']
    session = await get_session(request)
    await saml.ensure_logged_in(request)

    user_role = await saml.get_role_id(request)

    if not has_download_permission(user_role):
      return aiohttp_jinja2.render_template('error404.html', request,
                                            {'include_nav': True})

    try:
      search_range, records_per_page = page_bounds(1)

      get_microservice_info = get_microservice_records(
          "iattable", user_filter=search_range)
      get_microservice_info_json = get_microservice_info.json()

      if len(get_microservice_info_json) > 0:
        microservice_sum = get_microservice_info_json[0].get(
            'total_records', 0)

        # If there are more than 0 people in iat
        # then get_employee_info is set to everyone (max is total number of employees)
        search_range = {'rangeHigh': microservice_sum, 'rangeLow': 0}
        get_microservice_info = get_microservice_records(
            "iattable", search_range)
        get_microservice_info_json = get_microservice_info.json()

        field_classes = get_fields(microservice_name)

        html_microservice_records = get_table_records(
            field_classes,
            get_microservice_info_json,
            remove_html=True,
        )
        html_headers = get_table_headers(
            field_classes,
            remove_html=True,
        )

    except ClientResponseError as ex:
      client_response_error(ex, request)

    if get_microservice_info.status_code == 200:

      headers = ""
      for html_header in html_headers:
        headers = headers + str(html_header.get('value')) + " , "
      headers = headers[:-3]

      rows = ""
      for record in html_microservice_records:
        rows = str(rows) + "\n"
        for each_array in record.get('tds'):
          rows = str(rows) + str(each_array.get('value')) + " , "
        rows = rows[:-3]

      if microservice_name == "iattable":
        path = "/tmp/fsdrui_assets/"

        # Create unique file name
        file_name = f'{uuid.uuid4()}.csv'
        session['file_download_full_path'] = path + file_name

        with open(path + file_name, "w+") as of:
          of.write(str(headers))
          of.write(str(rows))

        download_location = "/fsdrui_assets/" + file_name
      else:
        logger.warn(f"Unknown download type: {microservice_name}")

      return {
          'download_location': download_location,
      }
    else:
      logger.warn('Database is down', client_ip=request['client_ip'])
      flash(request, NO_EMPLOYEE_DATA)
      raise HTTPFound(request.app.router['MainPage:get'].url_for())
