from aiohttp.web import HTTPFound, RouteTableDef
from aiohttp_utils.routing import add_resource_context, add_route_context
from pathlib import Path
from structlog import get_logger

from .employeehandler import employee_routes
from .handler import static_routes
from .saml import saml_routes
from .downloadshandler import downloads_routes
from .microserviceshandler import microservices_handler_routes
from .customsqlhandler import customsql_handler_routes
from .customsqlchoicehandler import customsql_choice_handler_routes

extra_routes = RouteTableDef()

logger = get_logger('fsdr-ui')


@extra_routes.get('/')
async def root(request):
  raise HTTPFound(request.app.router['sso'].url_for())


def setup(app, url_path_prefix):
  """Set up routes as resources so we can use the `Index:get` notation for URL lookup."""

  p = Path("/tmp/fsdrui_assets/")
  p.mkdir(parents=True, exist_ok=True)

  app.router.add_static("/fsdrui_assets/", p)

  combined_routes = [
      *extra_routes,
      *employee_routes,
      *static_routes,
      *saml_routes,
      *downloads_routes,
      *microservices_handler_routes,
      *customsql_handler_routes,
      *customsql_choice_handler_routes,
  ]

  module = ('app.handler')
  for route in combined_routes:
    prefix = url_path_prefix if route.kwargs.get('use_prefix', True) else ''
    if route.method == "*":
      with add_resource_context(app, module=module,
                                url_prefix=prefix) as new_resource:
        new_resource(route.path, route.handler())
    else:
      with add_route_context(app, module=module,
                             url_prefix=prefix) as new_route:
        new_route(route.method, route.path, route.handler)
