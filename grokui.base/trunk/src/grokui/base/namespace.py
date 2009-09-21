"""Components to keep Grok UI releated stuff in a dedicated namespace.
"""
import grok

from zope.interface import Interface
from zope.traversing.interfaces import ITraversable
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.browser import applySkin

class GrokUILayer(grok.IDefaultBrowserLayer):
    """A basic layer for all Grok UI components.
    """
    pass

class GrokUISkin(grok.IDefaultBrowserLayer):
    """A skin for all Grok UI stuff.
    """
    grok.skin('GrokUISkin')


class GrokUINamespace(grok.MultiAdapter):
    grok.name('grokui')
    grok.provides(ITraversable)
    grok.adapts(Interface, IBrowserRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        applySkin(self.request, GrokUILayer)

    def traverse(self, name, ignore):
        return self.context
