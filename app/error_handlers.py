import aiohttp_jinja2 as jinja

from aiohttp import web
from aiohttp.client_exceptions import (ClientResponseError,
                                       ClientConnectorError,
                                       ClientConnectionError, ContentTypeError)

from . import saml

from structlog import get_logger

logger = get_logger('fsdr-ui')


def create_error_middleware(overrides):
  @web.middleware
  async def middleware_handler(request, handler):
    try:
      resp = await handler(request)
      override = overrides.get(resp.status)
      return await override(request) if override else resp
    except web.HTTPNotFound:
      index_resource = request.app.router['sso']
      if request.path + '/' == index_resource.canonical:
        logger.debug('redirecting to index', path=request.path)
        # TODO restore this once all routes are fully set up
        # raise web.HTTPMovedPermanently(index_resource.url_for())
        raise web.HTTPFound(index_resource.url_for())
      return await not_found_error(request)
    except web.HTTPForbidden:
      return await forbidden(request)
    except ClientConnectionError as ex:
      return await connection_error(request, ex.args[0])
    except ClientConnectorError as ex:
      return await connection_error(request, ex.os_error.strerror)
    except ContentTypeError as ex:
      return await payload_error(request, str(ex.request_info.url))
    except ClientResponseError:
      return await response_error(request)
    # TODO fallthrough error here

  return middleware_handler


def warn_invalid_login(request):
  logger.warn('Attempted to login with invalid user name and/or password',
              client_ip=request['client_ip'])
  flash(request, NO_EMPLOYEE_DATA)

  return aiohttp_jinja2.render_template('signin.html', request, {
      'page_title': 'Sign in',
      'include_nav': False
  })


def client_response_error(ex, request):
  # Moved from individual handlers to here
  if ex.status == 503:
    ip = request['client_ip']
    logger.warn('Server is unavailable', client_ip=ip)
    flash(request, SERVICE_DOWN_MSG)
    return jinja.render_template('error503.html', request,
                                 {'include_nav': False})
  else:
    raise ex


async def connection_error(request, message: str):
  logger.error('service connection error', exception=message)
  return jinja.render_template('error500.html',
                               request, {
                                   'page_title': 'FSDR - Server down',
                                   'include_nav': False
                               },
                               status=500)


async def payload_error(request, url: str):
  logger.error('service failed to return expected json payload', url=url)
  return jinja.render_template('error500.html',
                               request, {
                                   'page_title': 'FSDR - Server down',
                                   'include_nav': False
                               },
                               status=500)


async def response_error(request):
  return jinja.render_template('error500.html',
                               request, {
                                   'page_title': 'FSDR - Server down',
                                   'include_nav': False
                               },
                               status=500)


async def not_found_error(request):
  return jinja.render_template('error404.html',
                               request, {
                                   'request_path': request.path,
                                   'include_nav': False
                               },
                               status=404)


async def forbidden(request):
  return jinja.render_template('error403.html',
                               request, {'include_nav': False},
                               status=403)


def setup(app):
  overrides = {
      500: response_error,
      503: response_error,
      404: not_found_error,
  }
  error_middleware = create_error_middleware(overrides)
  app.middlewares.append(error_middleware)
