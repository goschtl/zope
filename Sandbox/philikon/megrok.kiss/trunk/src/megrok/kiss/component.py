from zope.publisher.browser import BrowserPage
from kss.core import KSSView
from kss.core.pluginregistry import KSSPluginError

# XXX for AjaxAction.url() method
import urllib
from zope import component
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.traversing.browser.absoluteurl import _safe as SAFE_URL_CHARACTERS

class AjaxAction(KSSView, BrowserPage):

    def __call__(self):
        self.action()
        return self.render()

    def action(self):
        raise NotImplementedError("AjaxAction subclasses should implement "
                                  "the 'action' method.")

    def __getattr__(self, name):
        try:
            return self.getCommandSet(name)
        except KSSPluginError:
            raise AttributeError(name)

    # XXX warning, code duplication from grok.View

    def url(self, obj=None, name=None):
        # if the first argument is a string, that's the name. There should
        # be no second argument
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
        url = component.getMultiAdapter((obj, self.request), IAbsoluteURL)()
        if name is None:
            # URL to obj itself
            return url
        # URL to view on obj
        return url + '/' + urllib.quote(name.encode('utf-8'),
                                        SAFE_URL_CHARACTERS)
