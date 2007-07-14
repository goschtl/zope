import zope.interface
import zope.component
from zope.publisher.interfaces import NotFound


from z3c.traverser.interfaces import IPluggableTraverser, ITraverserPlugin

class FormTraverser(object):
    zope.interface.implements(IPluggableTraverser)

    def publishTraverse(self, request, name):
        # Act like a pluggable traverser.
        for traverser in zope.component.subscribers(
                 (self, request), ITraverserPlugin):
            try:
                return traverser.publishTraverse(request, name)
            except NotFound:
                pass

        raise NotFound(self.context, name, request)
