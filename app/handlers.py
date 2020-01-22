import aiohttp_jinja2

import math
import re
import requests

from requests.auth import HTTPBasicAuth
from aiohttp.client_exceptions import (ClientConnectionError,
                                       ClientConnectorError,
                                       ClientResponseError)
from aiohttp.web import HTTPFound, RouteTableDef, json_response
from aiohttp_session import get_session
from structlog import get_logger

from . import (VERSION, INVALID_SIGNIN_MSG, NEED_TO_SIGN_IN_MSG, NO_EMPLOYEE_DATA, SERVICE_DOWN_MSG)
from .flash import flash
from .security import remember

logger = get_logger('fsdr-ui')
routes = RouteTableDef()
employee_count_base_url = "http://localhost:5678/fieldforce/employeeCount/"


def setup_request(request):
    request['client_ip'] = request.headers.get('X-Forwarded-For', None)


def log_entry(request, endpoint):
    method = request.method
    logger.info(f"received {method} on endpoint '{endpoint}'",
                method=request.method,
                path=request.path)


class View:
    """
    Common base class for views
    """

    @staticmethod
    def _handle_response(response):
        try:
            response.raise_for_status()
        except ClientResponseError as ex:
            if not ex.status == 404:
                logger.error('error in response',
                             url=response.url,
                             status_code=response.status)
            raise ex
        else:
            logger.debug('successfully connected to service',
                         url=str(response.url))

    async def _make_request(self,
                            request,
                            method,
                            url,
                            func,
                            auth=None,
                            json=None,
                            return_json=False):
        """
        :param request: The AIOHTTP user request, used for logging and app access
        :param method: The HTTP verb
        :param url: The target URL
        :param auth: Authorization
        :param json: JSON payload to pass as request data
        :param func: Function to call on the response
        :param return_json: If True, the response JSON will be returned
        """
        logger.debug('making request with handler',
                     method=method,
                     url=url,
                     handler=func.__name__)
        try:
            async with request.app.http_session_pool.request(
                    method, url, auth=auth, json=json, ssl=False) as resp:
                func(resp)
                if return_json:
                    return await resp.json()
                else:
                    return None
        except (ClientConnectionError, ClientConnectorError) as ex:
            logger.error('client failed to connect',
                         url=url,
                         client_ip=request['client_ip'])
            raise ex


@routes.view('/info', use_prefix=False)
class Info(View):
    async def get(self, request):
        setup_request(request)
        log_entry(request, 'info')
        info = {
            'name': 'respondent-home-ui',
            'version': VERSION,
        }
        if 'check' in request.query:
            info['ready'] = await request.app.check_services()
        return json_response(info)


async def store_successful_signin(auth_json, request):
    await remember(auth_json['userRole'], request)
    logger.debug('Sign in successful',
                 client_ip=request['client_ip'])
    session = await get_session(request)
    session['user_details'] = auth_json
    session['logged_in'] = True
    session.permamnent = False


def get_fsdr_signin(request, user, password):
    fsdr_service_pass = request.app['FSDR_SERVICE_URL_PASS']
    fsdr_service_user = request.app['FSDR_SERVICE_URL_USER']
    return requests.get(f'http://localhost:5678/userAuth/checkCredentials?password={password}&username={user}',
                        verify=False,
                        auth=HTTPBasicAuth(fsdr_service_user, fsdr_service_pass))


@routes.view('/signin')
class Login(View):
    @aiohttp_jinja2.template('signin.html')
    async def get(self, request):
        setup_request(request)
        log_entry(request, 'signin')

    @aiohttp_jinja2.template('signin.html')
    async def post(self, request):
        setup_request(request)
        log_entry(request, 'signin')
        data = await request.post()

        try:
            get_user_info = get_fsdr_signin(request, data.get('user'), data.get('password'))
            if get_user_info.status_code == 200:
                auth_json = get_user_info.json()
                await store_successful_signin(auth_json, request)
                raise HTTPFound(
                    request.app.router['MainPage:get'].url_for(page='1'))
            elif get_user_info.status_code == 401:
                logger.warn('Attempted to login with invalid user name and/or password',
                            client_ip=request['client_ip'])
                flash(request, INVALID_SIGNIN_MSG)
                return aiohttp_jinja2.render_template(
                    'signin.html',
                    request, {
                        'display_region': 'en',
                        'page_title': 'Sign in'
                    },
                    status=401)
            elif get_user_info == 403:
                return aiohttp_jinja2.render_template(
                    'error403.html'
                )
            elif get_user_info == 404:
                return aiohttp_jinja2.render_template(
                    'error404.html'
                )

        except ClientResponseError as ex:
            if ex.status == 401:
                logger.warn('Attempted sign in with incorrect details',
                            client_ip=request['client_ip'])
                flash(request, INVALID_SIGNIN_MSG)
                return aiohttp_jinja2.render_template(
                    'signin.html'
                )
            else:
                return aiohttp_jinja2.render_template(
                    'signin.html'
                )

        except ConnectionError:
            return aiohttp_jinja2.render_template(
                'error500.html'
            )


@routes.view('/index+{page}')
class MainPage(View):
    @aiohttp_jinja2.template('index.html')
    async def get(self, request):
        session = await get_session(request)
        page_number = int(request.match_info['page'])

        try:
            user_json = session['user_details']
            user_role = user_json['userRole']
        except ClientResponseError:
            flash(request, NEED_TO_SIGN_IN_MSG)
            raise HTTPFound(
                request.app.router['Login:get'].url_for())

        if session.get('logged_in'):
            setup_request(request)
            log_entry(request, 'start')

            try:
                employee_count = get_employee_count(request)
                max_page = int(employee_count.text) / 50
                if page_number >= max_page:
                    page_number = int(math.floor(max_page))
                else:
                    if page_number > 1:
                        low_value = 50 * page_number
                        high_value = low_value + 50
                    else:
                        low_value = page_number
                        high_value = 50
                    get_employee_info = get_employee_records(request, user_role, low_value, high_value)
                    get_job_roles = get_distinct_job_role(request)
            except ClientResponseError as ex:
                if ex.status == 503:
                    logger.warn('Server is unavailable',
                                client_ip=request['client_ip'])
                    flash(request, SERVICE_DOWN_MSG)
                    raise HTTPFound(
                        request.app.router.url_for('error503.html')
                    )
                else:
                    raise ex

            if get_employee_info.status_code == 200:
                employee_records_json = get_employee_info.json()
                job_role_json = get_job_roles.json()
                return {
                    'page_title': f'Field Force view for: {user_role}',
                    'employee_records': employee_records_json,
                    'page_number': page_number,
                    'last_page_number': int(math.floor(max_page)),
                    'distinct_job_roles': job_role_json
                }
            else:
                logger.warn('Database is down',
                            client_ip=request['client_ip'])
                flash(request, NO_EMPLOYEE_DATA)
                raise HTTPFound(
                    request.app.router['MainPage:get'].url_for(page=0))

        else:
            flash(request, NEED_TO_SIGN_IN_MSG)
            raise HTTPFound(
                request.app.router['Login:get'].url_for())


@routes.view('/indexsearch+{page}+{previous_query}+{retrieve_count}')
class SecondaryPage(View):
    @aiohttp_jinja2.template('index-search.html')
    async def post(self, request):
        session = await get_session(request)
        page_number = int(request.match_info['page'])
        data = await request.post()

        try:
            user_json = session['user_details']
            user_role = user_json['userRole']
        except ClientResponseError:
            flash(request, NEED_TO_SIGN_IN_MSG)
            raise HTTPFound(
                request.app.router['Login:get'].url_for())

        if session.get('logged_in'):
            setup_request(request)
            log_entry(request, 'start')

            try:
                user_filter = ''
                format_user_filter = ''
                previous_area = ''
                previous_selected = ''
                previous_surname = ''

                if data.get('select'):
                    previous_selected = data.get('select')
                    selected_job_role = '&jobRole=' + previous_selected
                    if user_filter == '':
                        user_filter = selected_job_role
                        format_user_filter = '?jobRole=' + previous_selected
                    else:
                        user_filter = user_filter + '&' + selected_job_role
                        format_user_filter = format_user_filter + '&jobRole=' + previous_selected

                if data.get('filter_area'):
                    previous_area = data.get('filter_area')
                    filter_area = '&area=' + previous_area
                    if user_filter == '':
                        user_filter = filter_area
                        format_user_filter = '?area=' + previous_area
                    else:
                        user_filter = user_filter + filter_area
                        format_user_filter = format_user_filter + '&area=' + previous_area

                if data.get('filter_surname'):
                    previous_surname = data.get('filter_surname')
                    filter_surname = '&workerName=' + previous_surname
                    if user_filter == '':
                        user_filter = filter_surname
                        format_user_filter = '?workerName=' + previous_surname
                    else:
                        user_filter = user_filter + filter_surname
                        format_user_filter = format_user_filter + '&workerName=' + previous_surname

                high_value, low_value, page_number, max_page = await self.allocate_search_ranges(request,
                                                                                                 format_user_filter,
                                                                                                 page_number)

                retrieve_employee_info = get_employee_records(request, user_role, low_value,
                                                              high_value, user_filter)
                get_job_roles = get_distinct_job_role(request)

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

            if retrieve_employee_info.status_code == 200:
                employee_records_json = retrieve_employee_info.json()
                job_role_json = get_job_roles.json()
                return {
                    'page_title': f'Field Force view for: {user_role}',
                    'employee_records': employee_records_json,
                    'page_number': page_number,
                    'last_page_number': int(math.floor(max_page)),
                    'distinct_job_roles': job_role_json,
                    'previous_selection': user_filter,
                    'previous_area': previous_area,
                    'previous_select': previous_selected,
                    'previous_surname_filter': previous_surname
                }
            else:
                logger.warn('Attempted to login with invalid user name and/or password',
                            client_ip=request['client_ip'])
                flash(request, NO_EMPLOYEE_DATA)
                return aiohttp_jinja2.render_template(
                    'signin.html',
                    request, {
                        'display_region': 'en',
                        'page_title': 'Sign in'
                    },
                    status=401)

        else:
            flash(request, NEED_TO_SIGN_IN_MSG)
            raise HTTPFound(
                request.app.router['Login:get'].url_for())

    @aiohttp_jinja2.template('index-search.html')
    async def get(self, request):
        session = await get_session(request)
        page_number = int(request.match_info['page'])
        previous_query = request.match_info['previous_query']

        try:
            user_json = session['user_details']
            user_role = user_json['userRole']
        except:
            flash(request, NEED_TO_SIGN_IN_MSG)
            raise HTTPFound(
                request.app.router['Login:get'].url_for())

        if session.get('logged_in'):
            setup_request(request)
            log_entry(request, 'start')

            try:
                user_filter = previous_query
                format_user_filter = previous_query.replace("&", "?", 1)

                high_value, low_value, page_number, max_page = await self.allocate_search_ranges(request,
                                                                                                 format_user_filter,
                                                                                                 page_number)

                retrieve_employee_info = get_employee_records(request, user_role, low_value,
                                                              high_value, user_filter)
                get_job_roles = get_distinct_job_role(request)
            except ClientResponseError as ex:
                if ex.status == 503:
                    logger.warn('Server is unavailable',
                                client_ip=request['client_ip'])
                    flash(request, SERVICE_DOWN_MSG)
                    raise HTTPFound(
                        request.app.router.url_for('error503.html')
                    )
                else:
                    raise ex

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

            if retrieve_employee_info.status_code == 200:
                previous_area = ''
                previous_selected = ''
                previous_surname = ''
                employee_records_json = retrieve_employee_info.json()
                job_role_json = get_job_roles.json()

                split_user_filter = user_filter.replace("&", "", 1)
                filter_form_list = re.split('&|=', split_user_filter)

                filter_form_dict = {filter_form_list[i]: filter_form_list[i + 1]
                                    for i in range(0, len(filter_form_list), 2)}

                if 'area' in filter_form_dict.keys():
                    previous_area = filter_form_dict['area']

                if 'jobRole' in filter_form_dict.keys():
                    previous_selected = filter_form_dict['jobRole']

                if 'workerName' in filter_form_dict.keys():
                    previous_surname = filter_form_dict['workerName']

                return {
                    'page_title': f'Field Force view for: {user_role}',
                    'employee_records': employee_records_json,
                    'page_number': int(page_number),
                    'last_page_number': int(math.floor(max_page)),
                    'distinct_job_roles': job_role_json,
                    'previous_selection': user_filter,
                    'previous_area': previous_area,
                    'previous_select': previous_selected,
                    'previous_surname_filter': previous_surname
                }
            else:
                logger.warn('Attempted to login with invalid user name and/or password',
                            client_ip=request['client_ip'])
                flash(request, NO_EMPLOYEE_DATA)
                return aiohttp_jinja2.render_template(
                    'signin.html',
                    request, {
                        'display_region': 'en',
                        'page_title': 'Sign in'
                    },
                    status=401)

        else:
            flash(request, NEED_TO_SIGN_IN_MSG)
            raise HTTPFound(
                request.app.router['Login:get'].url_for())

    async def allocate_search_ranges(self, request, user_filter, page_number):
        employee_count = get_employee_count(request, user_filter)

        max_page = int(employee_count.text) / 50
        if page_number >= max_page:
            page_number = int(math.floor(max_page))
        if page_number == 0:
            low_value = 1
            high_value = 50
        elif page_number > 1:
            low_value = 50 * page_number
            high_value = low_value + 50
        else:
            low_value = page_number
            high_value = 50
        return high_value, low_value, page_number, max_page


@routes.view("/employeeinformation/{employee_id}")
class EmployeeInformation(View):
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


def get_employee_count(request, retrieve_count=""):
    fsdr_service_pass = request.app['FSDR_SERVICE_URL_PASS']
    fsdr_service_user = request.app['FSDR_SERVICE_URL_USER']

    employee_count_url = employee_count_base_url + retrieve_count
    return requests.get(f'{employee_count_url}',
                        verify=False,
                        auth=HTTPBasicAuth(fsdr_service_user, fsdr_service_pass))


def get_distinct_job_role(request):
    fsdr_service_pass = request.app['FSDR_SERVICE_URL_PASS']
    fsdr_service_user = request.app['FSDR_SERVICE_URL_USER']
    return requests.get(f'http://localhost:5678/jobRoles/allJobRoles/distinct',
                        verify=False,
                        auth=HTTPBasicAuth(fsdr_service_user, fsdr_service_pass))


def get_employee_records(request, user_role, low_value, high_value, user_filter=""):
    fsdr_service_pass = request.app['FSDR_SERVICE_URL_PASS']
    fsdr_service_user = request.app['FSDR_SERVICE_URL_USER']
    return requests.get(
        f'http://localhost:5678/fieldforce/byType/byRangeAndUserFilter/?rangeHigh={high_value}&rangeLow={low_value}&type={user_role}{user_filter}',
        verify=False,
        auth=HTTPBasicAuth(fsdr_service_user, fsdr_service_pass))
