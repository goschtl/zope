from zope.interface import implements
from zope.component.exceptions import ComponentLookupError
from zope.component.interfaces import IUtilityService
from zope.component.servicenames import Utilities

from OFS.Folder import Folder
from Products.Five.interfaces import IServiceProvider
from Products.FiveTest.interfaces import IDummySite

class SimpleLocalUtilityService:
    implements(IUtilityService)

    def __init__(self, context):
        self.context = context

    def getUtility(self, interface, name=''):
        """See IUtilityService interface
        """
        c = self.queryUtility(interface, name)
        if c is not None:
            return c
        raise ComponentLookupError(interface, name)

    def queryUtility(self, interface, name='', default=None):
        """See IUtilityService interface
        """
        utilities = getattr(self.context, 'utilities')
        utility = utilities._getOb(name, None)
        if utility is None:
            return default
        if not interface.providedBy(utility):
            return default
        return utility

    def getUtilitiesFor(self, interface):
        utilities = getattr(self.context, 'utilities')
        for utility in utilities.objectValues():
            if interface.providedBy(utility):
                yield utility

    def getAllUtilitiesRegisteredFor(self, interface):
        return ()

class ServiceProvider:
    implements(IServiceProvider)

    def __init__(self, context):
        self.context = context

    def getService(self, name):
        if name in (Utilities,):
            return SimpleLocalUtilityService(self.context)
        raise ComponentLookupError, name

class DummySite(Folder):
    """A very dummy Site
    """
    implements(IDummySite)

def manage_addDummySite(self, id, REQUEST=None):
    """Add the dummy site."""
    id = self._setObject(id, DummySite(id))
    return ''
