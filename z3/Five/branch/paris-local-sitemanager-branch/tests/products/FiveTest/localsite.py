from zope.interface import implements
from zope.component.servicenames import Utilities
from zope.component.exceptions import ComponentLookupError
from zope.component import getGlobalServices
from zope.component.interfaces import IServiceService
from zope.component.interfaces import IUtilityService
from zope.component.exceptions import ComponentLookupError

from OFS.Folder import Folder
from Products.FiveTest.interfaces import IDummySite

class SimpleService:
    implements(IServiceService)

    def __init__(self, context):
        self.context = context

    def getServiceDefinitions(self):
        """Retrieve all Service Definitions

        Should return a list of tuples (name, interface)
        """
        return getGlobalServices().getServiceDefinitions()

    def getInterfaceFor(self, name):
        """Retrieve the service interface for the given name
        """
        return getGlobalServices().getInterfaceFor(name)

    def getService(self, name):
        """Retrieve a service implementation

        Raises ComponentLookupError if the service can't be found.
        """
        if name == Utilities:
            return SimpleLocalUtilityService(self.context)
        return getGlobalServices().getService(name)

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

class SimpleFiveSiteAdapter:

    def __init__(self, context):
        self.context = context

    def getSiteManager(self):
        return SimpleService(self.context)

    def setSiteManager(self, sm):
        return

class DummySite(Folder):
    """A very dummy Site
    """
    implements(IDummySite)

def manage_addDummySite(self, id, REQUEST=None):
    """Add the dummy site."""
    id = self._setObject(id, DummySite(id))
    return ''
