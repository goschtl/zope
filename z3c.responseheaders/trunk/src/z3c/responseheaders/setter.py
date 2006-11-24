from zope import interface
from zope import component
from zope.security.proxy import removeSecurityProxy
import interfaces

def onBrowserViewBeforeTraverse(obj, event):
    adapter = interfaces.IResponseHeaderSetter(obj, None)
    if adapter is None:
        return
    adapter.setHeaders()

class BaseSetter(object):

    interface.implements(interfaces.IResponseHeaderSetter)
    headers = []

    def __init__(self, context):
        self.context = context
        
    def setHeaders(self):
        request = removeSecurityProxy(self.context).request
        for name, value in self.headers:
            request.response.setHeader(name, value)

