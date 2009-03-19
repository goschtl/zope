import martian.util
import grokcore.component 
import z3c.flashmessage.interfaces

from zope import interface
from zope import component
from grok import Application
from grokcore.view import View, util
from grok.interfaces import IGrokView 
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
    implements(IGrokView, IPagelet)
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
 
    def application_url(self, name=None):
        """Return the URL of the nearest enclosing `grok.Application`."""
        obj = self.context
        while obj is not None:
            if isinstance(obj, Application):
                return self.url(obj, name)
            obj = obj.__parent__
        raise ValueError("No application found.")

    def flash(self, message, type='message'):
        """Send a short message to the user."""
        # XXX this has no tests or documentation, anywhere
        source = component.getUtility(
            z3c.flashmessage.interfaces.IMessageSource, name='session')
        source.send(message, type)


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


    def url(self, obj=None, name=None, data=None):
        """Return string for the URL based on the obj and name. The data
        argument is used to form a CGI query string.
        """
        if isinstance(obj, basestring):
            if name is not None:
                raise TypeError(
                    'url() takes either obj argument, obj, string arguments, '
                    'or string argument')
            name = obj
            obj = None

        if name is None and obj is None:
            # create URL to view itself
            obj = self
        elif name is not None and obj is None:
            # create URL to view on context
            obj = self.context

        if data is None:
            data = {}
        else:
            if not isinstance(data, dict):
                raise TypeError('url() data argument must be a dict.')

        return util.url(self.request, obj, name, data=data)	
