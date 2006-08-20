from zope import component
from zc.copyversion import interfaces
import zope.locking.interfaces
import zope.locking.tokens

@component.adapter(interfaces.ITokenEnforced, interfaces.IObjectVersionedEvent)
def freezer(obj, ev):
    util = component.getUtility(zope.locking.interfaces.ITokenUtility)
    token = util.get(obj)
    if token is not None:
        if zope.locking.interfaces.IEndable.providedBy(token):
            token.end()
        else:
            return
    util.register(zope.locking.tokens.Freeze(obj))
