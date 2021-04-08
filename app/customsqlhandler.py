import json
import math
import os

import aiohttp_jinja2

from aiohttp.client_exceptions import (ClientResponseError)
from aiohttp.web import HTTPFound, RouteTableDef
from aiohttp_session import get_session
from structlog import get_logger
from app.pageutils import page_bounds, get_page, result_message
from app.error_handlers import client_response_error, forbidden
from app.role_matchers import microservices_permissions
from app.microservice_views import get_views, get_html
from app.customsqlutils import get_database_fields

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
    get_customsql_records,
    get_microservice_records,
)

from . import (NEED_TO_SIGN_IN_MSG, NO_EMPLOYEE_DATA, SERVICE_DOWN_MSG)
from . import saml
from .flash import flash

import sys
import os

logger = get_logger('fsdr-ui')
customsql_handler_routes = RouteTableDef()


def setup_request(request):
  request['client_ip'] = request.headers.get('X-Forwarded-For', None)


def log_entry(request, endpoint):
  method = request.method
  logger.info(f"received {method} on endpoint '{endpoint}'",
              method=request.method,
              path=request.path)


@customsql_handler_routes.view('/customsql')
class CustomSQLStart:
  @aiohttp_jinja2.template('microservices.html')
  async def post(self, request):
    session = await get_session(request)
    data = await request.post()

    user_role = await saml.get_role_id(request)

    await saml.ensure_logged_in(request)

    if microservices_permissions(user_role, 'customsql') == False:
      request['client_ip'] = request.get('client_ip', "No IP Provided")
      return await forbidden(request)

    database_names, fields = await get_database_fields(request)
    page_number = get_page(request)

    checked_boxes = session.get('custom_sql_previous_checked_fields', [])

    client_input = {}
    all_input = {}
    field_classes = []
    error = ""
    for db_name in fields.keys():
      current_fieldset = fields.get(db_name)  # [Field, Field, Field...]
      for field in current_fieldset:
        field_classes.append(field)

      client_input[db_name] = []
      for each_field in current_fieldset:
        if each_field.unique_name.replace('.', '') in all_input:
          each_field.previous_value = all_input.get(
              each_field.unique_name.replace('.', ''))

        checkbox_present, filter_data = each_field.find_and_extract(data)
        all_input[each_field.unique_name.replace('.', '')] = filter_data
        if (each_field.unique_name.replace('.', '')
            in checked_boxes) or checkbox_present:

          client_input[db_name].append({
              each_field.unique_name.replace('.', '') + '_text_box':
              filter_data
          })
          checked_boxes.append(each_field.unique_name.replace('.', ''))
          each_field.show_as_table_header = True
          each_field.search_box_visible = True
        else:
          each_field.show_as_table_header = False
          each_field.search_box_visible = False

    # Load into classes
    for field in field_classes:
      if field.unique_name.replace('.', '') in all_input:
        if all_input.get(field.unique_name.replace(".", "")) != '':
          field.previous_value = all_input.get(
              field.unique_name.replace(".", ""))

      if field.unique_name.replace('.', '') in data:
        field.previous_value = data.get(field.unique_name.replace(".", ""))

    all_input.update(data)
    session['custom_sql_previous_filters'] = all_input
    session['custom_sql_previous_checked_fields'] = checked_boxes

    all_records = get_customsql_records(all_input)

    all_records_json = all_records.json()

    search_criteria = {}
    search_range, records_per_page = page_bounds(page_number)
    search_criteria.update(search_range)
    get_microservice_info_json = all_records_json

    if len(get_microservice_info_json) > 0:
      microservice_sum = get_microservice_info_json[0].get('total_records', 0)
      max_page = math.ceil(microservice_sum / records_per_page)
    else:
      microservice_sum = 0
      max_page = 1

    table_records = get_table_records(
        field_classes,
        get_microservice_info_json,
        custom_sql=True,
    )

    result_message_str = result_message(search_range, microservice_sum,
                                        "Custom SQL")

    table_headers = get_table_headers(field_classes)

    views, current_view_index = get_views(user_role, 'customsql')
    header_html = get_html(user_role, views)
    current_view = views[current_view_index]

    return {
        'views': views,
        'header_html': header_html,
        'current_view': current_view,
        'fields': fields,
        'database_names': database_names,
        'called_from_index': 'customsql',
        'Fields': field_classes,
        'result_message': result_message_str,
        'page_title': f'Custom SQL view for: {user_role}',
        'page_number': page_number,
        'last_page_number': max_page,
        'table_headers': table_headers,
        'table_records': table_records,
    }

  @aiohttp_jinja2.template('microservices.html')
  async def get(self, request):
    session = await get_session(request)
    data = await request.post()

    logger.error(f'GET got data:  {data}')

    user_role = await saml.get_role_id(request)

    await saml.ensure_logged_in(request)

    if microservices_permissions(user_role, 'customsql') == False:
      request['client_ip'] = request.get('client_ip', "No IP Provided")
      return await forbidden(request)

    database_names, fields = await get_database_fields(request)
    page_number = get_page(request)

    checked_boxes = session.get('custom_sql_previous_checked_fields', [])

    client_input = {}
    all_input = {}
    field_classes = []
    error = ""
    for db_name in fields.keys():
      current_fieldset = fields.get(db_name)  # [Field, Field, Field...]
      for field in current_fieldset:
        field_classes.append(field)

      client_input[db_name] = []
      for each_field in current_fieldset:
        checkbox_present, filter_data = each_field.find_and_extract(data)
        if each_field.unique_name.replace('.', '') in all_input:
          each_field.previous_value = all_input.get(
              each_field.unique_name.replace('.', ''))

        all_input[each_field.unique_name.replace(
            '.', '')] = filter_data if filter_data != None else ''
        if each_field.unique_name.replace('.', '') in checked_boxes:

          client_input[db_name].append({
              each_field.unique_name.replace('.', '') + '_text_box':
              filter_data
          })
          each_field.show_as_table_header = True
          each_field.search_box_visible = True
        else:
          each_field.show_as_table_header = False
          each_field.search_box_visible = False

    previous_input = session.get('custom_sql_previous_filters', {})

    for key in previous_input.keys():
      if key in all_input.keys():
        if all_input.get(key) == '':
          all_input[key] = all_input.get(key)

    all_input.update(previous_input)

    # Load into classes
    for field in field_classes:
      if field.unique_name.replace('.', '') in all_input.keys():
        if all_input.get(field.unique_name.replace('.', '')) != '':
          field.previous_value = all_input.get(
              field.unique_name.replace('.', ''))

      if field.unique_name.replace('.', '') in data:
        field.previous_value = data.get(field.unique_name.replace(".", ""))

    session['custom_sql_previous_filters'] = all_input
    session['custom_sql_previous_checked_fields'] = checked_boxes

    all_records = get_customsql_records(previous_input)
    all_records_json = all_records.json()

    search_criteria = {}
    search_range, records_per_page = page_bounds(page_number)
    search_criteria.update(search_range)
    get_microservice_info_json = all_records_json

    if len(get_microservice_info_json) > 0:
      microservice_sum = get_microservice_info_json[0].get('total_records', 0)
      max_page = math.ceil(microservice_sum / records_per_page)
    else:
      microservice_sum = 0
      max_page = 1

    table_records = get_table_records(
        field_classes,
        get_microservice_info_json,
        custom_sql=True,
    )

    result_message_str = result_message(search_range, microservice_sum,
                                        "Custom SQL")

    table_headers = get_table_headers(field_classes)

    views, current_view_index = get_views(user_role, 'customsql')
    header_html = get_html(user_role, views)
    current_view = views[current_view_index]

    return {
        'views': views,
        'header_html': header_html,
        'current_view': current_view,
        'fields': fields,
        'database_names': database_names,
        'called_from_index': 'customsql',
        'Fields': field_classes,
        'result_message': result_message_str,
        'page_title': f'Custom SQL view for: {user_role}',
        'page_number': page_number,
        'last_page_number': max_page,
        'table_headers': table_headers,
        'table_records': table_records,
    }
