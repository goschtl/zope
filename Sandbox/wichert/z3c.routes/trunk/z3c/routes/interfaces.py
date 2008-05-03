from zope.interface import Interface
from zope.interface import Attribute

class IRoutingRoot(Interface):
    """Mark an object as a possible root for route based traversing.
    """

    def routes():
        """Return all routes associated with this object."""


class IRoute(Interface):
    """Route.

    A route maps a URL path to an object and a view for it
    """

    route = Attribute("Route specifier")
    factory = Attribute("Object factory.")
    arguments = Attribute("Extra arguments passed to the object factory")

    def __init__(route, factory, **kwargs):
        """Create a new route."""


    def match(path, request):
        """Test if this route matches a given request.
        """

    def execute(request):
        """Execute this route.

        You may only call this method if match() has already been called
        and returned succes.
        """


