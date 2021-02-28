import json
import math

import aiohttp_jinja2

from aiohttp.client_exceptions import (ClientResponseError)
from aiohttp.web import HTTPFound, RouteTableDef
from aiohttp_session import get_session
from app.pageutils import page_bounds, get_page, result_message
from structlog import get_logger
from app.microservice_views import get_views, get_html

from app.searchcriteria import (store_search_criteria, retrieve_job_roles,
                                retrieve_assignment_statuses,
                                clear_stored_search_criteria)

from app.searchfunctions import (get_all_assignment_status,get_microservice_records,
                                 get_employee_records_no_device,
                                 employee_record_table,
                                 employee_table_headers,
                                 get_distinct_job_role_short)

from . import (NEED_TO_SIGN_IN_MSG, NO_EMPLOYEE_DATA, SERVICE_DOWN_MSG)
from . import saml
from .flash import flash
from flask import Flask

logger = get_logger('fsdr-ui')
search_routes = RouteTableDef()
app = Flask(__name__)


@search_routes.view('/search')
class Search:
  @aiohttp_jinja2.template('search.html')
  async def get(self, request):
    session = await get_session(request)

    await saml.ensure_logged_in(request)

    await clear_stored_search_criteria(session)
    user_role = await saml.get_role_id(request)

    try:
      get_job_roles = get_distinct_job_role_short()
      get_all_assignment_statuses = get_all_assignment_status()
    except ClientResponseError as ex:
      if ex.status == 503:
        logger.warn('Server is unavailable',
                    client_ip=request.get('client_ip', None))
        flash(request, SERVICE_DOWN_MSG)
        return aiohttp_jinja2.render_template('error503.html', request,
                                              {'include_nav': False})
      else:
        raise ex

    if get_job_roles.status_code == 200 and get_all_assignment_statuses.status_code == 200:

      job_role_json = retrieve_job_roles(get_job_roles, '')
      assignment_statuses_json = retrieve_assignment_statuses(
          get_all_assignment_statuses)

      views, current_view_index = get_views(user_role, None)
      header_html = get_html(user_role, views)

      return {
          'views': views,
          'header_html': header_html,
          'page_title': f'Field Force view for: {user_role}',
          'distinct_job_roles': job_role_json,
          'all_assignment_statuses': assignment_statuses_json,
      }
    else:
      raise Exception(str(get_job_roles.status_code) + " " +  str(get_job_roles)  + "  " + \
              str(get_all_assignment_statuses) + " " +  str(get_all_assignment_statuses.status_code))

      logger.warn('Database is down', client_ip=request.get('client_ip', None))
      flash(request, NO_EMPLOYEE_DATA)
      raise HTTPFound(request.app.router['MainPage:get'].url_for())


@search_routes.view('/search-results')
class SecondaryPage:
  @aiohttp_jinja2.template('search-results.html')
  async def post(self, request):
    session = await get_session(request)
    data = await request.post()

    user_role = await saml.get_role_id(request)

    await saml.ensure_logged_in(request)

    page_number = get_page(request)

    previous_assignment_selected = ''
    previous_jobrole_selected = ''
    previous_area = ''
    previous_surname = ''
    previous_firstname = ''
    previous_badge = ''
    previous_jobid = ''
    previous_user_missing_device = False

    try:
      if data.get('indexsearch') == '' or 'called_from_index' in request.query:
        from_index = 'true'
      else:
        from_index = 'false'

      search_criteria = {}

      if data.get('assignment_select'):
        previous_assignment_selected = data.get('assignment_select')
        search_criteria['assignmentStatus'] = data.get('assignment_select')

      if data.get('user_missing_device'):
        previous_user_missing_device = data.get('user_missing_device')
        search_criteria['user_missing_device'] = data.get(
            'user_missing_device')

      if data.get('job_role_select'):
        previous_jobrole_selected = data.get('job_role_select')
        search_criteria['job_role_short'] = data.get('job_role_select')

      if data.get('filter_area'):
        previous_area = data.get('filter_area')
        search_criteria['area'] = previous_area

      if data.get('filter_surname'):
        previous_surname = data.get('filter_surname')
        search_criteria['surname'] = previous_surname

      if data.get('filter_firstname'):
        previous_firstname = data.get('filter_firstname')
        search_criteria['firstName'] = previous_firstname

      if data.get('filter_badge'):
        previous_badge = data.get('filter_badge')
        search_criteria['badgeNumber'] = previous_badge

      if data.get('filter_jobid'):
        previous_jobid = data.get('filter_jobid')
        search_criteria['jobRoleId'] = previous_jobid

      if data.get('filter_email'):
        previous_email = data.get('filter_email')
        search_criteria['email'] = previous_email

      if search_criteria:
        await store_search_criteria(request, search_criteria)

      if search_criteria == '' and from_index == 'true':
        raise HTTPFound(request.app.router['MainPage:get'].url_for())
      elif search_criteria == '' and from_index == 'false':
        return aiohttp_jinja2.render_template('search.html',
                                              request,
                                              {'no_search_criteria': 'True'},
                                              status=405)

      search_range, records_per_page = page_bounds(page_number)
      search_criteria.update(search_range)

      if previous_user_missing_device != False:
        retrieve_employee_info = get_employee_records_no_device(
            search_criteria)
      else:
        retrieve_employee_info = get_microservice_records('index',search_criteria)

      if len(retrieve_employee_info.json()) > 0:
        emp_sum = retrieve_employee_info.json()[0].get('total_records', 0)
        max_page = math.ceil(emp_sum / records_per_page)
      else:
        emp_sum = 0
        max_page = 1

      if data.get('user_missing_device'):
        previous_user_missing_device = data.get('user_missing_device')

      get_job_roles = get_distinct_job_role_short()

    except ClientResponseError as ex:
      raise ex

    if retrieve_employee_info.status_code == 200:
      table_headers = employee_table_headers()

      employees_present = retrieve_employee_info.content
      if employees_present == b'[]':
        no_employee_data = 'true'
        employee_records = ''
      else:
        no_employee_data = 'false'
        employee_records = employee_record_table(retrieve_employee_info.json())

      job_role_short_json = retrieve_job_roles(get_job_roles,
                                               previous_jobrole_selected)

      views, current_view_index = get_views(user_role, None)
      header_html = get_html(user_role, views)

      return {
          'views': views,
          'header_html': header_html,
          'result_message': result_message(search_range, emp_sum,
                                           "Field Workers"),
          'called_from_index': False,
          'page_title': f'Field Force view for: {user_role}',
          'table_headers': table_headers,
          'employee_records': employee_records,
          'page_number': page_number,
          'last_page_number': int(math.floor(max_page)),
          'distinct_job_roles': job_role_short_json,
          'previous_selection': json.dumps(search_criteria),
          'previous_area': previous_area,
          'previous_assignment_selected': previous_assignment_selected,
          'previous_jobrole_selected': previous_jobrole_selected,
          'previous_firstname': previous_firstname,
          'previous_badge': previous_badge,
          'previous_jobid': previous_jobid,
          'previous_surname_filter': previous_surname,
          'no_employee_data': no_employee_data,
          'user_missing_device': previous_user_missing_device,
      }
    else:
      logger.warn('Attempted to login with invalid user name and/or password',
                  client_ip=request.get('client_ip', None))
      flash(request, NO_EMPLOYEE_DATA)

      return aiohttp_jinja2.render_template('signin.html',
                                            request, {
                                                'page_title': 'Sign in',
                                                'include_nav': False
                                            },
                                            status=401)

  @aiohttp_jinja2.template('search-results.html')
  async def get(self, request):
    session = await get_session(request)

    user_role = await saml.get_role_id(request)

    await saml.ensure_logged_in(request)

    page_number = get_page(request)

    if 'called_from_index' in request.query:
      from_index = request.query['called_from_index']
    else:
      from_index = False

    search_criteria = {}

    previous_assignment_selected = ''
    previous_jobrole_selected = ''
    previous_area = ''
    previous_surname = ''
    previous_firstname = ''
    previous_badge = ''
    previous_jobid = ''
    previous_user_missing_device = False

    try:
      if session.get('assignmentStatus'):
        previous_assignment_selected = session['assignmentStatus']
        search_criteria['assignmentStatus'] = previous_assignment_selected

      if session.get('job_role_short'):
        previous_jobrole_selected = session['job_role_short']
        search_criteria['job_role_short'] = previous_jobrole_selected

      if session.get('user_missing_device'):
        previous_user_missing_device = session.get('user_missing_device')
        search_criteria['user_missing_device'] = session.get(
            'user_missing_device')

      if session.get('area'):
        previous_area = session['area']
        search_criteria['area'] = previous_area

      if session.get('surname'):
        previous_surname = session['surname']
        search_criteria['surname'] = previous_surname

      if session.get('firstName'):
        previous_firstname = session['firstName']
        search_criteria['firstName'] = previous_firstname

      if session.get('badgeNumber'):
        previous_badge = session['badgeNumber']
        search_criteria['badgeNumber'] = previous_badge

      if session.get('jobRoleId'):
        previous_jobid = session['jobRoleId']
        search_criteria['jobRoleId'] = previous_jobid

      search_range, records_per_page = page_bounds(page_number)
      search_criteria.update(search_range)

      if previous_user_missing_device != False:
        retrieve_employee_info = get_employee_records_no_device(
            search_criteria)
      else:
        retrieve_employee_info = get_microservice_records('index',search_criteria)

      if len(retrieve_employee_info.json()) > 0:
        emp_sum = retrieve_employee_info.json()[0].get('total_records', 0)
        max_page = math.ceil(emp_sum / records_per_page)
      else:
        emp_sum = 0
        max_page = 1

      get_job_roles = get_distinct_job_role_short()

    except ClientResponseError as ex:
      if ex.status == 503:
        logger.warn('Server is unavailable', client_ip=request['client_ip'])
        flash(request, SERVICE_DOWN_MSG)
        return aiohttp_jinja2.render_template('error503.html', request,
                                              {'include_nav': False})
      else:
        raise ex

    except ClientResponseError as ex:
      raise ex

    if retrieve_employee_info.status_code == 200:
      table_headers = employee_table_headers()

      employee_records = employee_record_table(retrieve_employee_info.json())

      job_role_json = retrieve_job_roles(get_job_roles,
                                         previous_jobrole_selected)

      views, current_view_index = get_views(user_role, None)
      header_html = get_html(user_role, views)

      return {
          'views': views,
          'header_html': header_html,
          'result_message': result_message(search_range, emp_sum,
                                           "Field Workers"),
          'called_from_index': False,
          'page_title': f'Field Force view for: {user_role}',
          'table_headers': table_headers,
          'employee_records': employee_records,
          'page_number': int(page_number),
          'last_page_number': int(math.floor(max_page)),
          'distinct_job_roles': job_role_json,
          'previous_selection': json.dumps(search_criteria),
          'previous_area': previous_area,
          'previous_assignment_selected': previous_assignment_selected,
          'previous_jobrole_selected': previous_jobrole_selected,
          'previous_firstname': previous_firstname,
          'previous_badge': previous_badge,
          'previous_jobid': previous_jobid,
          'previous_surname_filter': previous_surname,
          'previous_user_missing_device': previous_user_missing_device,
          'user_missing_device': previous_user_missing_device,
      }
    else:
      logger.warn('Attempted to login with invalid user name and/or password',
                  client_ip=request['client_ip'])
      flash(request, NO_EMPLOYEE_DATA)

      raise Exception(str(retrieve_employee_info.status_code))

      return aiohttp_jinja2.render_template('signin.html', request, {
          'page_title': 'Sign in',
          'include_nav': False
      })
