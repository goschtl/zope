import Acquisition
from AccessControl import ClassSecurityInfo, getSecurityManager
from zExceptions import Unauthorized
from Globals import InitializeClass

class BrowserView(Acquisition.Explicit):
    security = ClassSecurityInfo()

    def __init__(self, context, request):
        self.context = context
        self.request = request

    # XXX do not create any methods on the subclass called index_html,
    # as this makes Zope 2 traverse into that first!

    def __call__(self, *args, **kw):
        # XXX this is definitely not the way Zope 3 does it..
        if hasattr(self, 'index'):
            attr = 'index'
        else:
            attr = self.__page_attribute__
        meth = getattr(self, attr)
        security_manager = getSecurityManager()
        if not security_manager.validate(meth, self, attr, meth):
            raise Unauthorized
        if attr == '__call__':
            raise AttributeError("__call__")
        elif attr == 'index':
            return meth(self, *args, **kw)
        return meth(*args, **kw)

InitializeClass(BrowserView)
