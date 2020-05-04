import aiohttp_jinja2

import requests

from aiohttp.client_exceptions import (ClientResponseError)

from aiohttp.web import HTTPFound, RouteTableDef
from aiohttp_session import get_session
from requests.auth import HTTPBasicAuth
from structlog import get_logger

from app.searchcriteria import clear_stored_search_criteria
from app.utils import FSDR_USER, FSDR_URL, FSDR_PASS
from . import (INVALID_SIGNIN_MSG, SOMETHING_WENT_WRONG)
from .flash import flash
from .security import remember

import requests

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

    await clear_stored_search_criteria(session)

def get_fsdr_signin( user, password):
    credentials = {'password': password, 'username': user}
    return requests.post(FSDR_URL + f'/userAuth/checkCredentials', data=credentials,
                         verify=False,
                         auth=HTTPBasicAuth(FSDR_USER, FSDR_PASS))


@credential_routes.view('/')
class Redirect:
    async def get(self, request):
        raise HTTPFound(request.app.router['Login:get'].url_for())


@credential_routes.view('/signin')
class Login:
    @aiohttp_jinja2.template('signin.html')
    async def get(self, request):
        setup_request(request)
        log_entry(request, 'signin')
        return aiohttp_jinja2.render_template(
            'signin.html',
            request, {
                'page_title': 'Sign in',
                'include_nav': False
            })

    @aiohttp_jinja2.template('signin.html')
    async def post(self, request):
        setup_request(request)
        log_entry(request, 'signin')
        data = await request.post()

        try:
            get_user_info = get_fsdr_signin(data.get('user'), data.get('password'))
            if get_user_info.status_code == 200:
                auth_json = get_user_info.json()
                await store_successful_signin(auth_json, request)
                raise HTTPFound(
                    request.app.router['MainPage:get'].url_for())
            elif get_user_info.status_code == 401:
                logger.warn('Attempted to login with invalid user name and/or password',
                            client_ip=request['client_ip'])
                flash(request, INVALID_SIGNIN_MSG)
                return aiohttp_jinja2.render_template(
                    'signin.html',
                    request, {
                        'page_title': 'Sign in',
                        'include_nav': False
                    },
                    status=401)
            elif get_user_info == 404:
                return aiohttp_jinja2.render_template(
                    'error404.html',
                    request, {
                        'include_nav': False
                    })
            else:
                logger.warn('Something went wrong. Please try again.',
                            client_ip=request['client_ip'])
                flash(request, SOMETHING_WENT_WRONG)
                return aiohttp_jinja2.render_template(
                    'signin.html',
                    request, {
                        'include_nav': False
                    })

        except ClientResponseError:
            logger.warn('Something went wrong. Please try again.',
                        client_ip=request['client_ip'])
            flash(request, SOMETHING_WENT_WRONG)
            return aiohttp_jinja2.render_template(
                'signin.html',
                request, {
                    'include_nav': False
                })

        except requests.exceptions.ConnectionError:
            logger.warn('Service is down',
                        client_ip=request['client_ip'])
            return aiohttp_jinja2.render_template(
                'error500.html',
                request, {
                    'page_title': 'FSDR - Server down',
                    'include_nav': False
                })


@credential_routes.view('/logout')
class Logout:
    @aiohttp_jinja2.template('logout.html')
    async def get(self, request):
        session = await get_session(request)
        await clear_stored_search_criteria(session)
        session.pop('logged_in', None)
        return aiohttp_jinja2.render_template(
            'logout.html',
            request, {
                'page_title': 'FSDR - Signed out',
                'include_nav': False
            },
            status=200)
