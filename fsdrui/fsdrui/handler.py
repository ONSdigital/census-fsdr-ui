from aiohttp.web import RouteTableDef, json_response
from structlog import get_logger

from . import (VERSION)

logger = get_logger('fsdr-ui')
static_routes = RouteTableDef()


def setup_request(request):
  request['client_ip'] = request.headers.get('X-Forwarded-For', None)


def log_entry(request, endpoint):
  method = request.method
  logger.info(f"received {method} on endpoint '{endpoint}'",
              method=request.method,
              path=request.path)


@static_routes.view('/info', use_prefix=False)
class Info():
  async def get(self, request):
    setup_request(request)
    log_entry(request, 'info')
    info = {
        'name': 'fsdr-ui',
        'version': VERSION,
    }
    if 'check' in request.query:
      info['ready'] = await request.app.check_services()
    return json_response(info)
