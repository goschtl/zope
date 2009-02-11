
from zope.interface import adapts
from zope.interface import implements
from zope.publisher.interfaces import IWSGIApplication


class Traverser(object):
    """Traverses the object graph based on the traversal stack.

    Requires 'zope.request' in the WSGI environment.
    """
    implements(IWSGIApplication)
    adapts(IWSGIApplication)

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request = environ['zope.request']
        self.traverse(request)
        return self.app(environ, start_response)

    def traverse(self, request):
        traversal_stack = request.traversal_stack
        traversal_hooks = request.traversal_hooks
        traversed = request.traversed

        root_name, obj = traversed[-1]
        prev_object = None

        while True:
            if obj is not prev_object:
                # Call hooks (but not more than once).
                for hook in traversal_hooks:
                    hook(request, obj)

            if not traversal_stack:
                break

            prev_object = obj

            # Traverse to the next step.
            name = traversal_stack.pop()
            obj = self.traverse_name(obj, name)
            traversed.append((name, obj))

    def traverse_name(self, obj, name):
        pass


class HTTPTraverser(Traverser):
    implements(IWSGIApplication)
    adapts(IWSGIApplication)
    request_type = IHTTPRequest

