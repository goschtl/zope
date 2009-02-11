
from zope.event import notify
from zope.interface import adapts
from zope.interface import implements
from zope.publisher.interfaces import IWSGIApplication
from zope.publisher.interfaces.event import BeforeTraverseEvent
from zope.publisher.interfaces.event import EndRequestEvent


class EventNotifier(object):
    """Fires request-related events.

    Fires are BeforeTraverseEvent and EndRequestEvent at the appropriate
    times.
    """
    implements(IWSGIApplication)
    adapts(IWSGIApplication)

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request = environ['zope.request']
        request.traversal_hooks.append(self.fireBeforeTraverse)
        try:
            return self.app(environ, start_response)
        finally:
            if request.traversed:
                name, ob = request.traversed[-1]
            else:
                ob = None
            notify(EndRequestEvent(ob, request))

    def fireBeforeTraverse(self, request, ob):
        notify(BeforeTraverseEvent(ob, request))
