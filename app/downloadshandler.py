import json
import math
import uuid
from io import StringIO

import aiohttp_jinja2

from multidict import MultiDict
from aiohttp import web
from aiohttp.client_exceptions import ClientResponseError
from aiohttp.web import HTTPFound, RouteTableDef
from aiohttp_session import get_session
from structlog import get_logger
from app.microservice_tables import get_table_records, get_table_headers
from app.role_matchers import has_download_permission
from app.error_handlers import client_response_error, warn_invalid_login
from app.pageutils import page_bounds
from datetime import datetime
from app.searchfunctions import get_microservice_records

from app.microservice_tables import (
    get_table_headers,
    get_table_records,
    get_fields,
)

from . import NEED_TO_SIGN_IN_MSG, NO_EMPLOYEE_DATA, SERVICE_DOWN_MSG
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

    if not has_download_permission(user_role, microservice_name):
      return aiohttp_jinja2.render_template('error403.html', request,
                                            {'include_nav': True})

    try:
      search_range, records_per_page = page_bounds(1)

      get_microservice_info = get_microservice_records(
          microservice_name, user_filter=search_range)
      get_microservice_info_json = get_microservice_info.json()

      if len(get_microservice_info_json) > 0:
        microservice_sum = get_microservice_info_json[0].get(
            'total_records', 0)

        # If there are more than 0 people in Microservice
        # then get_employee_info is set to everyone (max is total number of employees)
        search_range = {'rangeHigh': microservice_sum, 'rangeLow': 0}
        get_microservice_info = get_microservice_records(
            microservice_name, search_range)
        get_microservice_info_json = get_microservice_info.json()

        field_classes = await get_fields(microservice_name, request)

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

      with StringIO(newline='') as csvfile:
        spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)

        spamwriter.writerow(html_headers)
        spamwriter.writerows(html_microservice_records)  

        logger.error(f'HTML HEADERS:  "{html_headers}", HTML ROWS: "{html_microservice_records}"')

        # Create unique file name
        today = datetime.today().strftime('%Y-%m-%d')
        file_name = f'{microservice_name}{today}-{uuid.uuid4()}.csv'


        return web.Response(
          headers=MultiDict({'Content-Disposition': f'attachment; filename="{file_name}"'}),
          body=csvfile.getvalue()
        )
    else:
      logger.warn('Database is down', client_ip=request['client_ip'])
      flash(request, NO_EMPLOYEE_DATA)
      raise HTTPFound(request.app.router['MainPage:get'].url_for())
