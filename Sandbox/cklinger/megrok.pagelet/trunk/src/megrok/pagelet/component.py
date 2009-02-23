import martian.util
import grokcore.component 

from zope import interface
from zope import component
from grokcore.view import View
from grokcore.view import interfaces
from martian.error import GrokImportError
from zope.interface import implements
from zope.component import getMultiAdapter
from z3c.pagelet.interfaces import IPagelet
from zope.publisher.browser import BrowserPage
from z3c.template.interfaces import ILayoutTemplate
from grokcore.view.interfaces import IGrokView

class Layout(object):
    """ A basic class for Layouts"""
    pass


class Pagelet(BrowserPage):
    implements(interfaces.IGrokView, IPagelet)
    template = None
    layout = None

    def __init__(self, context, request):
        super(Pagelet, self).__init__(context, request)
        self.__name__ = self.__view_name__
        self.static = component.queryAdapter(
            self.request,
            interface.Interface,
            name=self.module_info.package_dotted_name
            )
  
    def default_namespace(self):
        namespace = {}
        namespace['context'] = self.context
        namespace['request'] = self.request
        namespace['static'] = self.static
        namespace['view'] = self
        return namespace

    def namespace(self):
        return {}
  
    def update(self):
        pass

    def render(self):
        # We don not work with IContentTemplate for now
        # We use instead our grok.View behavior with the associated
        # Templates

        return self.template.render(self)

    def __call__(self):
        """Calls update and returns the layout template which calls render."""
        self.update()
        if self.layout is None:
            layout = component.getMultiAdapter(
                (self.context, self.request), ILayoutTemplate)
            return layout(self)
        return self.layout()
