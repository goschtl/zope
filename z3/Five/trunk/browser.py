import Acquisition
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class BrowserView(Acquisition.Explicit):
    security = ClassSecurityInfo()
    
    def __init__(self, context, request):
        self.context = context
        self.request = request

    # XXX do not create any methods on the subclass called index_html,
    # as this makes Zope 2 traverse into that first!
    
    def __call__(self, *args, **kw):
        attr = self.__page_attribute__
        if attr == '__call__':
            raise AttributeError("__call__")
        meth = getattr(self, attr)
        return meth(*args, **kw)
    
InitializeClass(BrowserView)
