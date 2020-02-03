import aiohttp_jinja2

import requests

from datetime import datetime

from requests.auth import HTTPBasicAuth
from aiohttp.client_exceptions import (ClientResponseError)

from aiohttp.web import HTTPFound, RouteTableDef
from aiohttp_session import get_session
from structlog import get_logger

from . import (INVALID_SIGNIN_MSG, NEED_TO_SIGN_IN_MSG, NO_EMPLOYEE_DATA)
from .flash import flash

logger = get_logger('fsdr-ui')
employee_routes = RouteTableDef()


def setup_request(request):
    request['client_ip'] = request.headers.get('X-Forwarded-For', None)


def log_entry(request, endpoint):
    method = request.method
    logger.info(f"received {method} on endpoint '{endpoint}'",
                method=request.method,
                path=request.path)


@employee_routes.view("/employeeinformation/{employee_id}")
class EmployeeInformation():
    @aiohttp_jinja2.template('employee-information.html')
    async def get(self, request):
        employee_id = request.match_info['employee_id']
        session = await get_session(request)
        try:
            user_json = session['user_details']
            user_role = user_json['userRole']
        except:
            flash(request, NEED_TO_SIGN_IN_MSG)
            raise HTTPFound(
                request.app.router['Login:get'].url_for())

        if session.get('logged_in'):
            try:
                get_employee_info = self.get_employee_information(request, user_role, employee_id)
                get_employee_device = self.get_employee_device(request, employee_id)
                get_employee_history = self.get_employee_history_information(request, user_role, employee_id)
            except ClientResponseError as ex:
                if ex.status == 404:
                    logger.warn('attempt to use an invalid access code',
                                client_ip=request['client_ip'])
                    flash(request, INVALID_SIGNIN_MSG)
                    return aiohttp_jinja2.render_template(
                        'index.html',
                        request, {
                        },
                        status=401)
                else:
                    raise ex

            if get_employee_info.status_code == 200:
                employee_info = get_employee_info.json()
                employee_history = []
                device_info = []

                if employee_info['ingestDate']:
                    employee_info['ingestDate'] = self.format_to_uk_dates(
                            employee_info['ingestDate'][:-9])

                if get_employee_history.status_code == 200:
                    if get_employee_history.content != b'':
                        employee_history_json = get_employee_history.json()

                        for employee_history_dict in employee_history_json:
                            if employee_history_dict['ingestDate']:
                                employee_history_dict['ingestDate'] = self.format_to_uk_dates(
                                    employee_history_dict['ingestDate'][:10])
                                employee_history.append(employee_history_dict.copy())

                if get_employee_device.status_code == 200:
                    if get_employee_device.content != b'':
                        device_info_json = get_employee_device.json()
                        device_info.append(device_info_json.copy())

                last_job_role = employee_info['lastRoleId']
                job_role_info = employee_info['jobRoles']
                relevant_job_role = ''

                for job_role in job_role_info:
                    if job_role['active']:
                        relevant_job_role = job_role

                if relevant_job_role == '':
                    for job_role in job_role_info:
                        if job_role['uniqueRoleId'] == last_job_role:
                            relevant_job_role = job_role

                if relevant_job_role:
                    if relevant_job_role['contractStartDate']:
                        relevant_job_role['contractStartDate'] = self.format_to_uk_dates(
                            relevant_job_role['contractStartDate'])
                    if relevant_job_role['contractEndDate']:
                        relevant_job_role['contractEndDate'] = self.format_to_uk_dates(
                            relevant_job_role['contractEndDate'])
                    if relevant_job_role['operationalEndDate']:
                        relevant_job_role['operationalEndDate'] = self.format_to_uk_dates(
                            relevant_job_role['operationalEndDate'])

                try:
                    return {
                        'page_title': f'Worker details for: {employee_id}',
                        'employee_device': device_info,
                        'employee_history': employee_history,
                        'employee_job_role': relevant_job_role,
                        'employee_job_role_history': job_role_info,
                        'employee_record': employee_info
                    }
                except ValueError:
                    return {
                        'page_title': f'Worker details for: {employee_id}',
                        'employee_record': employee_info,
                        'employee_device': "No device"
                    }
            else:
                logger.warn('Attempted to login with invalid user name and/or password',
                            client_ip=request['client_ip'])
                flash(request, NO_EMPLOYEE_DATA)
                return aiohttp_jinja2.render_template(
                    'index.html',
                    request, {
                        'display_region': 'en',
                        'page_title': 'Sign in'
                    },
                    status=401)
        else:
            flash(request, NEED_TO_SIGN_IN_MSG)
            raise HTTPFound(
                request.app.router['Login:get'].url_for())

    def get_employee_information(self, request, user_role, employee_id):
        fsdr_service_pass = request.app['FSDR_SERVICE_URL_PASS']
        fsdr_service_user = request.app['FSDR_SERVICE_URL_USER']
        return requests.get(f'http://localhost:5678/fieldforce/byId/{user_role}/{employee_id}',
                            verify=False,
                            auth=HTTPBasicAuth(fsdr_service_user, fsdr_service_pass))

    def get_employee_history_information(self, request, user_role, employee_id):
        fsdr_service_pass = request.app['FSDR_SERVICE_URL_PASS']
        fsdr_service_user = request.app['FSDR_SERVICE_URL_USER']
        return requests.get(f'http://localhost:5678/fieldforce/historyById/{user_role}/{employee_id}',
                            verify=False,
                            auth=HTTPBasicAuth(fsdr_service_user, fsdr_service_pass))

    def get_employee_device(self, request, employee_id):
        fsdr_service_pass = request.app['FSDR_SERVICE_URL_PASS']
        fsdr_service_user = request.app['FSDR_SERVICE_URL_USER']
        return requests.get(f'http://localhost:5678/devices/byEmployee/getPhoneDevice/{employee_id}',
                            verify=False,
                            auth=HTTPBasicAuth(fsdr_service_user, fsdr_service_pass))

    def format_to_uk_dates(self, date):
        date_to_format = datetime.strptime(date, '%Y-%m-%d')
        formatted_date = date_to_format.strftime('%d/%m/%Y')
        return formatted_date
