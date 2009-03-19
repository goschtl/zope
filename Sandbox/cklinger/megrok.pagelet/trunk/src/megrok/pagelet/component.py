import martian.util
import grokcore.component 

from zope import interface
from zope import component
from grok import Application
from grokcore.view import View, util
from grok.interfaces import IGrokView 
from martian.error import GrokImportError
from zope.interface import implements
from zope.component import getMultiAdapter
from zope.publisher.browser import BrowserPage
from z3c.template.interfaces import ILayoutTemplate
from grokcore.view.interfaces import IGrokView
import grok


class Layout(object):
    """ A basic class for Layouts"""
    pass

class Pagelet(grok.View):
    """ This is the BaseClass for the Pagelets"""
    grok.baseclass()
    layout = None

    def render(self):
        return self._render_template()

    render.base_method = True

    def __call__(self):
        """Calls update and returns the layout template which calls render."""
        self.update()
        if self.layout is None:
            layout = component.getMultiAdapter(
                (self.context, self.request), ILayoutTemplate)
            return layout(self)
        return self.layout()

