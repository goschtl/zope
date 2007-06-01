from zope.interface import Interface
from zope.component.interfaces import ComponentLookupError
from zope.component.registry import Components

from z3c.componentdebug.lookup import VerboseComponentLookupError

origGetUtility = Components.getUtility
def getUtility(self, provided, name=u''):
    try:
        return origGetUtility(self, provided, name)
    except ComponentLookupError:
        raise VerboseComponentLookupError(
            False, provided, name, self,
            methods=['registeredUtilities'])

origGetAdapter = Components.getAdapter
def getAdapter(self, object, interface=Interface, name=u''):
    try:
        return origGetAdapter(self, object, interface, name)
    except ComponentLookupError:
        raise VerboseComponentLookupError(
            (object,), interface, name, self,
            methods=['registeredAdapters'])

origGetMultiAdapter = Components.getMultiAdapter
def getMultiAdapter(self, objects, interface=Interface, name=u''):
    try:
        return origGetMultiAdapter(self, objects, interface, name)
    except ComponentLookupError:
        raise VerboseComponentLookupError(
            objects, interface, name, self,
            methods=['registeredAdapters'])

def patch():
    Components.getUtility = getUtility
    Components.getAdapter = getAdapter
    Components.getMultiAdapter = getMultiAdapter

def cleanup():
    Components.getUtility = origGetUtility
    Components.getAdapter = origGetAdapter
    Components.getMultiAdapter = origGetMultiAdapter
