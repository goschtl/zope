"""More verbose ComponentLookupError reporting."""

from zope.interface import Interface
from zope.component.interfaces import ComponentLookupError
from zope.component import _api

from z3c.componentdebug.component import Registrations, all_methods

class VerboseComponentLookupError(ComponentLookupError):

    def __init__(self, objects=False, provided=False, name=False,
                 context=None, methods=all_methods):
        self.registrations = Registrations(objects, provided, name,
                                           context, methods)
        ComponentLookupError.__init__(
            self, '\n'.join(
                (str(self.registrations),
                 str([i for i in self.registrations.byObjects()]))))

origGetAdapterInContext = _api.getAdapterInContext
def getAdapterInContext(object, interface, context):
    try:
        origGetAdapterInContext(object, interface, context)
    except ComponentLookupError:
        raise VerboseComponentLookupError(
            (object,), interface, u'', context)

origGetAdapter = _api.getAdapter
def getAdapter(object, interface=Interface, name=u'', context=None):
    try:
        origGetAdapter(object, interface, name, context)
    except ComponentLookupError:
        raise VerboseComponentLookupError(
            (object,), interface, name, context)

origGetMultiAdapter = _api.getMultiAdapter
def getMultiAdapter(objects, interface=Interface, name=u'', context=None):
    try:
        origGetMultiAdapter(objects, interface, name, context)
    except ComponentLookupError:
        raise VerboseComponentLookupError(
            objects, interface, name, context)

origGetUtility = _api.getUtility
def getUtility(interface, name='', context=None):
    try:
        origGetUtility(interface, name, context)
    except ComponentLookupError:
        raise VerboseComponentLookupError(
            False, interface, name, context)

def patch():
    _api.getAdapterInContext = getAdapterInContext
    _api.getAdapter = getAdapter
    _api.getMultiAdapter = getMultiAdapter
    _api.getUtility = getUtility

def cleanup():
    _api.getAdapterInContext = origGetAdapterInContext
    _api.getAdapter = origGetAdapter
    _api.getMultiAdapter = origGetMultiAdapter
    _api.getUtility = origGetUtility
