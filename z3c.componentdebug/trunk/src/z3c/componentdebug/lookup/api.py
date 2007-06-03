from zope.interface import Interface
from zope.component.interfaces import ComponentLookupError
from zope.component import _api
from zope import component

from z3c.componentdebug.lookup import VerboseComponentLookupError

default = object()

origGetAdapterInContext = _api.getAdapterInContext
def getAdapterInContext(object, interface, context):
    adapter = _api.queryAdapterInContext(
        object, interface, name, context=context, default=default)
    if adapter is default:
        raise VerboseComponentLookupError(
            (object,), interface, u'', context,
            methods=['registeredAdapters'])
    return adapter

origGetAdapter = _api.getAdapter
def getAdapter(object, interface=Interface, name=u'', context=None):
    adapter = _api.queryAdapter(
        object, interface, name, context=context, default=default)
    if adapter is default:
        raise VerboseComponentLookupError(
            (object,), interface, u'', context,
            methods=['registeredAdapters'])
    return adapter

origGetMultiAdapter = _api.getMultiAdapter
def getMultiAdapter(objects, interface=Interface, name=u'',
                    context=None):
    adapter = _api.queryMultiAdapter(
        objects, interface, name, context=context, default=default)
    if adapter is default:
        raise VerboseComponentLookupError(
            objects, interface, name, context,
            methods=['registeredAdapters'])
    return adapter

origGetUtility = _api.getUtility
def getUtility(interface, name='', context=None):
    utility = _api.queryUtility(provided, name, default=default)
    if utility is default:
        raise VerboseComponentLookupError(
            False, interface, name, context,
            methods=['registeredUtilities'])
    return utility

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
