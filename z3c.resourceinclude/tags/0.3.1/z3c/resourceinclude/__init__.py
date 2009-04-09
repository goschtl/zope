import zope.interface
import zope.security.management
import zope.security.interfaces

from zope.publisher.interfaces import IRequest
from zope.deprecation import deprecated

def getRequest():
    try:
        i = zope.security.management.getInteraction() # raises NoInteraction
    except zope.security.interfaces.NoInteraction:
        return

    for p in i.participations:
        if IRequest.providedBy(p):
            return p

def include(*ifaces):
    request = getRequest()

    for iface in ifaces:
        zope.interface.alsoProvides(request, iface)

def provide(iface):
    deprecated('provide', 'The ``provide``-method is deprecated; use ``include`` instead.')
    include(iface)
