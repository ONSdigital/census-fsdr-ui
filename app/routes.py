from aiohttp.web import HTTPFound, RouteTableDef
from aiohttp_utils.routing import add_resource_context, add_route_context

from .employeehandler import employee_routes
from .indexhandler import index_route
from .handler import static_routes
from .saml import saml_routes
from .searchhandler import search_routes
from .interfaceactiontablehandler import interface_action_handler_table_route

extra_routes = RouteTableDef()


@extra_routes.get('/')
async def root(request):
    raise HTTPFound(request.app.router['sso'].url_for())


def setup(app, url_path_prefix):
    """Set up routes as resources so we can use the `Index:get` notation for URL lookup."""

    combined_routes = [
        *extra_routes, *employee_routes, *index_route, *static_routes,
        *search_routes, *saml_routes
    ]

    module = ('app.handler')
    for route in combined_routes:
        prefix = url_path_prefix if route.kwargs.get('use_prefix',
                                                     True) else ''
        if route.method == "*":
            with add_resource_context(app, module=module,
                                      url_prefix=prefix) as new_resource:
                new_resource(route.path, route.handler())
        else:
            with add_route_context(app, module=module,
                                   url_prefix=prefix) as new_route:
                new_route(route.method, route.path, route.handler)
