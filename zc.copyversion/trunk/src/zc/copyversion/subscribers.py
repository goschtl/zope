from zope import component
from zc.copyversion import interfaces
import zope.locking.interfaces
import zope.locking.tokens

@component.adapter(interfaces.IObjectVersionedEvent)
def freezer(ev):
    util = component.getUtility(zope.locking.interfaces.ITokenUtility)
    obj = ev.object
    token = util.get(obj)
    if token is not None:
        if zope.locking.interfaces.IEndable.providedBy(token):
            token.end()
        else:
            return
    util.register(zope.locking.tokens.Freeze(obj))
