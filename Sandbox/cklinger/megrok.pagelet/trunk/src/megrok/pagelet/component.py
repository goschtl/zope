import martian.util
import grokcore.component 

from zope import interface
from zope import component
from grokcore.view import View
from grokcore.view import interfaces
from martian.error import GrokImportError
from zope.interface import implements
from zope.component import getMultiAdapter
from zope.publisher.browser import BrowserPage
from z3c.template.interfaces import ILayoutTemplate
from grokcore.view.interfaces import IGrokView

class LayoutView(object):
    pass


class Pagelet(BrowserPage):
    implements(interfaces.IGrokView)
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
   
    def update(self):
        pass

    def render(self):
        # render content template
        if self.template is None:
            template = zope.component.getMultiAdapter(
                (self, self.request), IContentTemplate)
            return template(self)
        return self.template()

    def __call__(self):
        """Calls update and returns the layout template which calls render."""
        self.update()
        if self.layout is None:
            layout = component.getMultiAdapter(
                (self.context, self.request), ILayoutTemplate)
            return layout(self)
        return self.layout()
