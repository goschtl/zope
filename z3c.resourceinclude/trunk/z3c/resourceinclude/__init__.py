import zope.interface
import zope.security.management
import zope.security.interfaces

from zope.publisher.interfaces import IRequest

def getRequest():
    try:
        i = zope.security.management.getInteraction() # raises NoInteraction
    except zope.security.interfaces.NoInteraction:
        return

    for p in i.participations:
        if IRequest.providedBy(p):
            return p

def provide(iface):
    request = getRequest()
    zope.interface.alsoProvides(request, iface)
