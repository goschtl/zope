from zope import interface
from zope import component
from zope.security.proxy import removeSecurityProxy
import interfaces

def onBrowserViewBeforeTraverse(obj, event):
    setter = component.queryMultiAdapter(
        (obj, event.request), interfaces.IResponseHeaderSetter)
    if setter is None:
        return
    setter.setHeaders()

class BaseSetter(object):

    interface.implements(interfaces.IResponseHeaderSetter)
    headers = []

    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    def setHeaders(self):
        for name, value in self.headers:
            self.request.response.setHeader(name, value)

