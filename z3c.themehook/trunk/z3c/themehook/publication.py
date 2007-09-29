import zope.interface
import zope.component
from zope.app.publication.requestpublicationfactories import BrowserFactory
from zope.security.checker import selectChecker
from zope.publisher.interfaces.browser import IBrowserRequest

from zope.app.publication.browser import BrowserPublication
from zope.publisher.publish import mapply

from interfaces import IPublicationObjectCaller

class PluggedBrowserPublication(BrowserPublication):

    def callObject(self, request, ob):
        adapter = zope.component.queryMultiAdapter((ob, request), 
                                                   IPublicationObjectCaller)
        if adapter is None:
            # Fallback to a hook that just makes a mapply:
            adapter = DefaultPublicationObjectCaller(ob, request)
        return adapter()

class PluggedBrowserFactory(BrowserFactory):

    def __call__(self):
        request, publication = super(PluggedBrowserFactory, self).__call__()
        return request, PluggedBrowserPublication

class DefaultPublicationObjectCaller(object):
    zope.interface.implements(IPublicationObjectCaller)
    zope.component.adapts(None, IBrowserRequest)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    def __call__(self):
        return mapply(self.context, 
                      self.request.getPositionalArguments(), 
                      self.request)
        
