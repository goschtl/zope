from zope.interface import Interface
from zope.component.interfaces import ComponentLookupError
from zope.component.registry import Components

from z3c.componentdebug.lookup import VerboseComponentLookupError

default = object()

origGetUtility = Components.getUtility
def getUtility(self, provided, name=u''):
    utility = self.queryUtility(provided, name, default=default)
    if utility is default:
        raise VerboseComponentLookupError(
            False, provided, name, self,
            methods=['registeredUtilities'])
    return utility

origGetAdapter = Components.getAdapter
def getAdapter(self, object, interface=Interface, name=u''):
    adapter = self.queryAdapter(object, interface, name,
                                default=default)
    if adapter is default:
        raise VerboseComponentLookupError(
            (object,), interface, name, self,
            methods=['registeredAdapters'])
    return adapter

origGetMultiAdapter = Components.getMultiAdapter
def getMultiAdapter(self, objects, interface=Interface, name=u''):
    adapter = self.queryMultiAdapter(objects, interface, name,
                                     default=default)
    if adapter is default:
        raise VerboseComponentLookupError(
            objects, interface, name, self,
            methods=['registeredAdapters'])
    return adapter

def patch():
    Components.getUtility = getUtility
    Components.getAdapter = getAdapter
    Components.getMultiAdapter = getMultiAdapter

def cleanup():
    Components.getUtility = origGetUtility
    Components.getAdapter = origGetAdapter
    Components.getMultiAdapter = origGetMultiAdapter
