import aiohttp_jinja2
from aiohttp.client_exceptions import (ClientResponseError)
from aiohttp.web import HTTPFound, RouteTableDef
from aiohttp_session import get_session
from structlog import get_logger

from app.employee_view_functions import get_employee_information, get_employee_history_information, get_employee_device
from app.employee_view_router import get_employee_tabs
from app.historytab import history_tab
from app.tabutils import format_to_uk_dates
from app.microservice_views import get_views, get_html
from . import (NEED_TO_SIGN_IN_MSG, NO_EMPLOYEE_DATA)
from . import saml
from . import role_matchers
from .flash import flash

employee_routes = RouteTableDef()
logger = get_logger('fsdr-ui')


@employee_routes.view("/employeeinformation/{employee_id}")
class EmployeeInformation():
  @aiohttp_jinja2.template('employee-information.html')
  async def get(self, request):
    employee_id = request.match_info['employee_id']
    session = await get_session(request)

    await saml.ensure_logged_in(request)

    role_id = await saml.get_role_id(request)
    role = role_matchers.get_role(role_id)

    try:
      get_employee_info = get_employee_information(role, employee_id)
      get_employee_devices = get_employee_device(employee_id)
      get_employee_history = get_employee_history_information(
          role, employee_id)
    except ClientResponseError as ex:
      if ex.status == 500:
        client_ip = request.get('client_ip', None)
        logger.warn('Service is down', client_ip=client_ip)
        return aiohttp_jinja2.render_template('error500.html', request, {
            'page_title': 'FSDR - Server down',
            'include_nav': False
        })
      else:
        raise ex

    if get_employee_info.status_code != 200:
      logger.warn('Attempted to login with invalid user name and/or password',
                  client_ip=request.get('client_ip', None))
      flash(request, NO_EMPLOYEE_DATA)
      return aiohttp_jinja2.render_template('signin.html',
                                            request, {
                                                'page_title': 'Sign in',
                                                'include_nav': False
                                            },
                                            status=401)

    employee_info = get_employee_info.json()
    employee_history = []
    device_info = []
    employee_name = employee_info['firstName'] + ' ' + employee_info['surname']
    employee_status = employee_info['status']
    if role_matchers.hr_combined_regex.match(role_id):
      employee_badge = employee_info['idBadgeNo']
    else:
      employee_badge = ''

    employee_info['address'] = ' '.join(
        v for v in (employee_info.get('address1', None),
                    employee_info.get('address2', None)) if v is not None)

    if role_matchers.logi_combined_regex.match(role_id):
      if employee_info['ingestDate']:
        employee_info['ingestDate'] = format_to_uk_dates(
            employee_info['ingestDate'])

    if get_employee_history.status_code == 200:
      if get_employee_history.content != b'':

        employee_history_json = get_employee_history.json()

        for employee_history_dict in employee_history_json:
          if employee_history_dict['ingestDate']:
            employee_history_dict['ingestDate'] = format_to_uk_dates(
                employee_history_dict['ingestDate'])
            employee_history.append(employee_history_dict.copy())

    if get_employee_devices.status_code == 200:
      if get_employee_devices.content != b'':
        device_info_json = get_employee_devices.json()
        device_info = device_info + device_info_json.copy()

    last_job_role = employee_info['lastRoleId']

    job_role = employee_info.get('jobRole', "-")

    employee_tabs = get_employee_tabs(role_id, employee_info, job_role,
                                      device_info)

    device_headers = []
    device_data = []

    for tabs in employee_tabs:
      if 'all_info' in tabs:
        employee_info = tabs['all_info']
      else:
        for device_table in tabs:
          if 'headers' in device_table:
            device_headers = device_table['headers']
          if 'tds' in device_table:
            device_data = device_table['tds']

    employee_history_tabs = history_tab(role_id, job_role, employee_history)

    if (not role_matchers.hr_combined_regex.match(role_id)
        ) and not (role_matchers.logi_combined_regex.match(role_id)):

      job_role_history_header = []
      job_role_history_data = []

      history_header = ""
      history_data = ""

      for employee_history in employee_history_tabs[0]:
        if 'headers' in employee_history:
          history_header = employee_history['headers']
        if 'tds' in employee_history:
          history_data = employee_history['tds']

      for employee_history in employee_history_tabs[1]:
        if 'headers' in employee_history:
          job_role_history_header = employee_history['headers']
        if 'tds' in employee_history:
          job_role_history_data = employee_history['tds']

    else:
      for employee_history in employee_history_tabs[0]:
        if 'headers' in employee_history:
          history_header = employee_history['headers']
        if 'tds' in employee_history:
          history_data = employee_history['tds']

      job_role_history_header = []
      job_role_history_data = []

    if role_matchers.hr_combined_regex.match(role_id):
      page_title = f'Employee: {employee_name}'
    else:
      page_title = f'Employee: {employee_name} {f"({employee_badge})" if employee_badge else ""}'

    extract_type = role_matchers.get_role(role_id).extract_type

    views, current_view_index = get_views(role_id, None)
    header_html = get_html(role_id, views)

    try:
      return {
          'header_html': header_html,
          'user_role': role_id,
          'extract_type': extract_type,
          'page_title': page_title,
          'device_headers': device_headers,
          'device_data': device_data,
          'employment_history_headers': history_header,
          'employment_history_data': history_data,
          'employee_job_role_history_header': job_role_history_header,
          'employee_job_role_history_data': job_role_history_data,
          'employee_history': employee_history,
          'employee_job_role': job_role,
          'employee_job_role_history': job_role,
          'employee_record': employee_info,
          'employee_status': employee_status,
      }
    except ValueError:
      return {
          'page_title': page_title,
          'employee_status': employee_status,
          'employee_record': employee_info,
          'employee_device': "No device",
          'dst_download': role_matchers.has_download_permission(user_role),
      }
