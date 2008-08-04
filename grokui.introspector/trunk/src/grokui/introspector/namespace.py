import grok

from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.traversing.interfaces import ITraversable
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.browser import applySkin
from zope.location.location import locate

class IntrospectorLayer(IDefaultBrowserLayer):
    """A basic layer for all introspection stuff.
    """
    pass

class IntrospectorSkin(grok.IDefaultBrowserLayer):
    """A skin for all introspection stuff.
    """
    grok.skin('IntrospectorSkin')


class GrokIntrospectorNamespace(grok.MultiAdapter):
    grok.name('inspect')
    grok.provides(ITraversable)
    grok.adapts(Interface, IBrowserRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    def traverse(self, name, ignore):
        applySkin(self.request, IntrospectorLayer)
        return self.context
