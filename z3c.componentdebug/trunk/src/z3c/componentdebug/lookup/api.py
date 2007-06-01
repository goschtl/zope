from zope.interface import Interface
from zope.component.interfaces import ComponentLookupError
from zope.component import _api
from zope import component

from z3c.componentdebug.lookup import VerboseComponentLookupError

origGetAdapterInContext = _api.getAdapterInContext
def getAdapterInContext(object, interface, context):
    try:
        return origGetAdapterInContext(object, interface, context)
    except ComponentLookupError:
        raise VerboseComponentLookupError(
            (object,), interface, u'', context,
            methods=['registeredAdapters'])

origGetAdapter = _api.getAdapter
def getAdapter(object, interface=Interface, name=u'', context=None):
    try:
        return origGetAdapter(object, interface, name, context)
    except ComponentLookupError:
        raise VerboseComponentLookupError(
            (object,), interface, name, context,
            methods=['registeredAdapters'])

origGetMultiAdapter = _api.getMultiAdapter
def getMultiAdapter(objects, interface=Interface, name=u'',
                    context=None):
    try:
        return origGetMultiAdapter(objects, interface, name, context)
    except ComponentLookupError:
        raise VerboseComponentLookupError(
            objects, interface, name, context,
            methods=['registeredAdapters'])

origGetUtility = _api.getUtility
def getUtility(interface, name='', context=None):
    try:
        return origGetUtility(interface, name, context)
    except ComponentLookupError:
        raise VerboseComponentLookupError(
            False, interface, name, context,
            methods=['registeredUtilities'])

def patch():
    _api.getAdapterInContext = getAdapterInContext
    _api.getAdapter = getAdapter
    _api.getMultiAdapter = getMultiAdapter
    _api.getUtility = getUtility

    component.getAdapterInContext = getAdapterInContext
    component.getAdapter = getAdapter
    component.getMultiAdapter = getMultiAdapter
    component.getUtility = getUtility

def cleanup():
    _api.getAdapterInContext = origGetAdapterInContext
    _api.getAdapter = origGetAdapter
    _api.getMultiAdapter = origGetMultiAdapter
    _api.getUtility = origGetUtility

    component.getAdapterInContext = origGetAdapterInContext
    component.getAdapter = origGetAdapter
    component.getMultiAdapter = origGetMultiAdapter
    component.getUtility = origGetUtility
