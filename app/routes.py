from aiohttp.web import HTTPFound, RouteTableDef
from aiohttp_utils.routing import add_resource_context, add_route_context
from pathlib import Path
from structlog import get_logger

from .employeehandler import employee_routes
from .indexhandler import index_route
from .handler import static_routes
from .saml import saml_routes
from .searchhandler import search_routes
from .interfaceactiontablehandler import interface_action_handler_table_routes
from .devicetablehandler import device_table_handler_routes
from .downloadshandler import downloads_routes
from .microserviceshandler import microservices_handler_routes

extra_routes = RouteTableDef()

logger = get_logger('fsdr-ui')


@extra_routes.get('/')
async def root(request):
  raise HTTPFound(request.app.router['sso'].url_for())


def setup(app, url_path_prefix):
  """Set up routes as resources so we can use the `Index:get` notation for URL lookup."""

  path = str(Path(__file__).resolve()) + "/app/"
  path = "/opt/ui/app/assets/"

  # TODO remove show_index, or set to False
  app.router.add_static("/assets", path, show_index=True)

  combined_routes = [
      *extra_routes,
      *employee_routes,
      *index_route,
      *static_routes,
      *search_routes,
      *saml_routes,
      *interface_action_handler_table_routes,
      *device_table_handler_routes,
      *downloads_routes,
      *microservices_handler_routes,
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
