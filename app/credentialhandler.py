import aiohttp_jinja2

import requests

from aiohttp.client_exceptions import (ClientResponseError)

from aiohttp.web import HTTPFound, RouteTableDef
from aiohttp_session import get_session
from requests.auth import HTTPBasicAuth
from structlog import get_logger

from . import (INVALID_SIGNIN_MSG)
from .flash import flash
from .security import remember

logger = get_logger('fsdr-ui')
credential_routes = RouteTableDef()


def setup_request(request):
    request['client_ip'] = request.headers.get('X-Forwarded-For', None)


def log_entry(request, endpoint):
    method = request.method
    logger.info(f"received {method} on endpoint '{endpoint}'",
                method=request.method,
                path=request.path)


async def store_successful_signin(auth_json, request):
    await remember(auth_json['userRole'], request)
    logger.debug('Sign in successful',
                 client_ip=request['client_ip'])
    session = await get_session(request)
    session['user_details'] = auth_json
    session['logged_in'] = True
    session.permamnent = False


def get_fsdr_signin(request, user, password):
    fsdr_service_pass = request.app['FSDR_SERVICE_PASS']
    fsdr_service_user = request.app['FSDR_SERVICE_USER']
    fsdr_service_url = request.app['FSDR_SERVICE_URL']
    credentials = {'password': password, 'username': user}
    return requests.post(fsdr_service_url + f'/userAuth/checkCredentials', data=credentials,
                         verify=False,
                         auth=HTTPBasicAuth(fsdr_service_user, fsdr_service_pass))


@credential_routes.view('/')
class Redirect:
    async def get(self, request):
        return aiohttp_jinja2.render_template(
            'signin.html',
            request, {
                'page_title': 'Sign in'
            }
        )


@credential_routes.view('/signin')
class Login:
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
                        'page_title': 'Sign in'
                    },
                    status=401)
            elif get_user_info == 403:
                return aiohttp_jinja2.render_template(
                    'error403.html',
                    request, {
                    })
            elif get_user_info == 404:
                return aiohttp_jinja2.render_template(
                    'error404.html',
                    request, {
                    })

        except ClientResponseError as ex:
            if ex.status == 401:
                logger.warn('Attempted sign in with incorrect details',
                            client_ip=request['client_ip'])
                flash(request, INVALID_SIGNIN_MSG)
                return aiohttp_jinja2.render_template(
                    'signin.html',
                    request, {
                    })
            else:
                return aiohttp_jinja2.render_template(
                    'signin.html',
                    request, {
                    })

        except requests.exceptions.ConnectionError:
            logger.warn('Service is down',
                        client_ip=request['client_ip'])
            return aiohttp_jinja2.render_template(
                'error500.html',
                request, {
                    'page_title': 'FSDR - Server down'
                })


@credential_routes.view('/logout')
class Logout:
    @aiohttp_jinja2.template('logout.html')
    async def get(self, request):
        session = await get_session(request)
        session.pop('logged_in', None)
        return aiohttp_jinja2.render_template(
            'logout.html',
            request, {
                'page_title': 'FSDR - Signed out'
            },
            status=200)
