from zope.interface import implements
from zope.component import adapts
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.http import IHTTPRequest
from z3c.routes.interfaces import IRoutingRoot


class RouteTraverser(object):
    implements(IPublishTraverse)
    adapts(IRoutingRoot, IHTTPRequest)

    def __init__(self, context, request):
        self.context=context
        self.request=request


    def publishTraverse(self, request, name):
        path=name+"/".join(request.getTraversalStack())
        for route in IRoutingRoot(self.context).routes():
            if route.match(path, request):
                return route.execute(request)
        else:
            raise NotFound(self.context, name)



