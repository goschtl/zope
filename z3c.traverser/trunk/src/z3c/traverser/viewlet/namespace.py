from zope.traversing.namespace import SimpleHandler
from zope import component
from zope.publisher.interfaces import NotFound
from zope.viewlet.interfaces import IViewletManager

class ViewletManagerHandler(SimpleHandler):

    def __init__(self, context, request=None):
        self.context = context
        self.request = request

    def traverse(self, name, ignored):
        provider = component.queryMultiAdapter(
            (self.context.__parent__,
             self.request, self.context),
            IViewletManager, name)
        if provider is None:
            raise NotFound(self.context, name, self.request)
        return provider


class ViewletHandler(SimpleHandler):

    def __init__(self, context, request=None):
        self.context = context
        self.request = request

    def traverse(self, name, ignored):
        # Try to look up the provider.
        viewlet = self.context.get(name)
        if viewlet is None:
            raise NotFound(self.context, name, self.request)
        return viewlet
