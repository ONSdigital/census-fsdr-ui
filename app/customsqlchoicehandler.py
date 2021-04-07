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
    get_microservice_records, )

from . import (NEED_TO_SIGN_IN_MSG, NO_EMPLOYEE_DATA, SERVICE_DOWN_MSG)
from . import saml
from .flash import flash

import sys
import os

logger = get_logger('fsdr-ui')
customsql_choice_handler_routes = RouteTableDef()


def setup_request(request):
  request['client_ip'] = request.headers.get('X-Forwarded-For', None)


def log_entry(request, endpoint):
  method = request.method
  logger.info(f"received {method} on endpoint '{endpoint}'",
              method=request.method,
              path=request.path)


@customsql_choice_handler_routes.view('/customsqlchoice')
class CustomSQLChoice:
  @aiohttp_jinja2.template('error404.html')
  async def post(self, request):
    session = await get_session(request)
    data = await request.post()

    user_role = await saml.get_role_id(request)

    await saml.ensure_logged_in(request)

    if microservices_permissions(user_role, 'customsql') == False:
      request['client_ip'] = request.get('client_ip', "No IP Provided")
      return await forbidden(request)

    return {
        'page_title': f'Custom SQL view for: {user_role}',
    }

  @aiohttp_jinja2.template('customsqlstart.html')
  async def get(self, request):
    session = await get_session(request)
    user_role = await saml.get_role_id(request)

    await saml.ensure_logged_in(request)

    if microservices_permissions(user_role, 'customsql') == False:
      request['client_ip'] = request.get('client_ip', "No IP Provided")
      return await forbidden(request)

    database_names, fields = await get_database_fields(request)

    views, current_view_index = get_views(user_role, 'customsql')
    header_html = get_html(user_role, views)
    current_view = views[current_view_index]

    return {
        'views': views,
        'header_html': header_html,
        'current_view': current_view,
        'fields': fields,
        'database_names': database_names,
    }
