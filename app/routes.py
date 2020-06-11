from aiohttp_utils.routing import add_resource_context

from .credentialhandler import credential_routes
from .employeehandler import employee_routes
from .indexhandler import index_route
from .handler import static_routes
from .saml import saml_routes
from .searchhandler import search_routes


def setup(app, url_path_prefix):
    """Set up routes as resources so we can use the `Index:get` notation for URL lookup."""

    combined_routes = [*credential_routes, *employee_routes, *index_route, *static_routes, *search_routes, *saml_routes]

    for route in combined_routes:
        use_prefix = route.kwargs.get('use_prefix', True)
        prefix = url_path_prefix if use_prefix else ''
        with add_resource_context(app,
                                  module=('app.handler'),
                                  url_prefix=prefix) as new_route:
            new_route(route.path, route.handler())
