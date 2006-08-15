from zope import component
import zope.locking.interfaces
import zope.security.management

@component.adapter(zope.locking.interfaces.ITokenEvent)
def tokenSubscriber(ev):
    interaction = zope.security.management.queryInteraction()
    if interaction is not None:
        try:
            invalidateCache = interaction.invalidateCache
        except AttributeError:
            pass
        else:
            invalidateCache()
