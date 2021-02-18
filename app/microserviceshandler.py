import json
import math

import aiohttp_jinja2

from aiohttp.client_exceptions import (ClientResponseError)
from aiohttp.web import HTTPFound, RouteTableDef
from aiohttp_session import get_session
from structlog import get_logger
from app.pageutils import page_bounds, get_page, result_message
from app.error_handlers import client_response_error, forbidden
from app.role_matchers import download_permission, microservices_permissions

from app.microservice_tables import (
    get_table_headers,
    get_table_records,
    get_fields,
    get_fields_to_load,
    load_cookie_into_fields,
)

from app.searchcriteria import (
    store_search_criteria,
    load_search_criteria,
    clear_stored_search_criteria,
)

from app.searchfunctions import (
    get_microservice_records, )

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
    microservice_name = request.match_info['microservice_name']

    if 'clear' in microservice_name:
      microservice_name = microservice_name.replace('clear', '')
      await clear_stored_search_criteria(session, microservice_name)

    if microservices_permissions(user_role, microservice_name) == False:
      request['client_ip'] = request.get('client_ip', "No IP Provided")
      return await forbidden(request)

    microservice_title = microservice_name.replace("table", " Table").title()
    page_number = get_page(request)

    try:

      field_classes = get_fields(microservice_name)
      table_headers = get_table_headers(
          field_classes)  # formatted for table use
      fields_to_load = get_fields_to_load(field_classes)

      search_criteria, previous_criteria = load_search_criteria(
          data, fields_to_load)
      field_classes = load_cookie_into_fields(field_classes, search_criteria)

      if search_criteria:
        await store_search_criteria(request, previous_criteria, fields_to_load)

      if search_criteria == '' and from_index == 'true':
        raise HTTPFound(request.app.router['MicroservicesTable:get'].url_for())
      elif search_criteria == '' and from_index == 'false':
        return aiohttp_jinja2.render_template('search.html',
                                              request,
                                              {'no_search_criteria': 'True'},
                                              status=405)

      search_range, records_per_page = page_bounds(page_number)
      search_criteria.update(search_range)

      get_microservice_info = get_microservice_records(
          microservice_name, user_filter=search_criteria)
      get_microservice_info_json = get_microservice_info.json()

      if len(get_microservice_info_json) > 0:
        microservice_sum = get_microservice_info_json[0].get(
            'total_records', 0)
        max_page = math.ceil(microservice_sum / records_per_page)
      else:
        microservice_sum = 0
        max_page = 1

    except ClientResponseError as ex:
      return client_response_error(ex, request)

    if get_microservice_info.status_code == 200:
      # for 0 response st no_records true

      table_records = get_table_records(
          field_classes, get_microservice_info_json
      )  # database name field ([gsuite_status,...

      result_message_str = result_message(search_range, microservice_sum,
                                          microservice_title)

      return {
          'called_from_index': False,
          'Fields': field_classes,
          'microservice_name': microservice_name,
          'microservice_title': microservice_title,
          'result_message': result_message_str,
          'page_title': f'{microservice_title} view for: {user_role}',
          'dst_download': download_permission(user_role),
          'page_number': page_number,
          'last_page_number': max_page,
          'table_headers': table_headers,
          'table_records': table_records,
      }
    else:
      return warn_invalid_login(request)

  @aiohttp_jinja2.template('microservices.html')
  async def get(self, request):
    session = await get_session(request)

    user_role = await saml.get_role_id(request)

    await saml.ensure_logged_in(request)
    microservice_name = request.match_info['microservice_name']

    if 'clear' in microservice_name:
      microservice_name = microservice_name.replace('clear', '')
      await clear_stored_search_criteria(session, microservice_name)

    if microservices_permissions(user_role, microservice_name) == False:
      request['client_ip'] = request.get('client_ip', "No IP Provided")
      return await forbidden(request)

    microservice_title = microservice_name.replace("table", " Table").title()
    page_number = get_page(request)

    try:
      field_classes = get_fields(microservice_name)
      table_headers = get_table_headers(
          field_classes)  # formatted for table use
      fields_to_load = get_fields_to_load(field_classes)

      search_criteria, previous_criteria = load_search_criteria(
          session, fields_to_load)
      field_classes = load_cookie_into_fields(field_classes, search_criteria)

      search_range, records_per_page = page_bounds(page_number)
      search_criteria.update(search_range)

      get_microservice_info = get_microservice_records(
          microservice_name, user_filter=search_criteria)
      get_microservice_info_json = get_microservice_info.json()

      if len(get_microservice_info_json) > 0:
        microservice_sum = get_microservice_info_json[0].get(
            'total_records', 0)
        max_page = math.ceil(microservice_sum / records_per_page)
      else:
        microservice_sum = 0
        max_page = 1

    except ClientResponseError as ex:
      return client_response_error(ex, request)

    if get_microservice_info.status_code == 200:
      table_records = get_table_records(
          field_classes, get_microservice_info_json
      )  # database name field ([gsuite_status,...
      result_message_str = result_message(search_range, microservice_sum,
                                          microservice_title)
      return {
          'called_from_index': False,
          'Fields': field_classes,
          'microservice_name': microservice_name,
          'microservice_title': microservice_title,
          'result_message': result_message_str,
          'page_title': f'{microservice_title} view for: {user_role}',
          'dst_download': download_permission(user_role),
          'page_number': page_number,
          'last_page_number': max_page,
          'table_headers': table_headers,
          'table_records': table_records,
      }
    else:
      return warn_invalid_login(request)
