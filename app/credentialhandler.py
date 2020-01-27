import aiohttp_jinja2

import requests

from requests.auth import HTTPBasicAuth
from aiohttp.client_exceptions import (ClientResponseError)

from aiohttp.web import HTTPFound, RouteTableDef
from aiohttp_session import get_session
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
    fsdr_service_pass = request.app['FSDR_SERVICE_URL_PASS']
    fsdr_service_user = request.app['FSDR_SERVICE_URL_USER']
    return requests.get(f'http://localhost:5678/userAuth/checkCredentials?password={password}&username={user}',
                        verify=False,
                        auth=HTTPBasicAuth(fsdr_service_user, fsdr_service_pass))


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


@credential_routes.view('/logout')
class Logout:
    @aiohttp_jinja2.template('signin.html')
    async def get(self, request):
        session = await get_session(request)
        session.pop('logged_in', None)
        raise HTTPFound(request.app.router['Login:get'].url_for())
        # return aiohttp_jinja2.render_template((
        #     request.app.router['Login:get'].url_for()),
        #     request, {
        #         'signed_out': 'true'
        #     },
        # status=200)
