import aiohttp_jinja2

import requests

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
            except ClientResponseError as ex:
                if ex.status == 404:
                    logger.warn('attempt to use an invalid access code',
                                client_ip=request['client_ip'])
                    flash(request, INVALID_SIGNIN_MSG)
                    return aiohttp_jinja2.render_template(
                        'index.html',
                        request, {
                            'display_region': 'en',
                            'page_title': 'Start Census'
                        },
                        status=401)
                else:
                    raise ex

            if get_employee_info.status_code == 200:
                employee_info = get_employee_info.json()
                if get_employee_device.status_code == 200:
                    try:
                        device_info = get_employee_device.json()
                        return {
                            'page_title': f'Worker details for: {employee_id}',
                            'employee_record': employee_info,
                            'employee_device': device_info
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

    def get_employee_device(self, request, employee_id):
        fsdr_service_pass = request.app['FSDR_SERVICE_URL_PASS']
        fsdr_service_user = request.app['FSDR_SERVICE_URL_USER']
        return requests.get(f'http://localhost:5678/devices/byEmployee/getPhoneDevice/{employee_id}',
                            verify=False,
                            auth=HTTPBasicAuth(fsdr_service_user, fsdr_service_pass))
