##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Zope 3 Component Architecture

$Id: __init__.py,v 1.20 2004/03/06 00:38:47 jim Exp $
"""
import sys
import warnings
from zope.interface import moduleProvides, Interface
from zope.component.interfaces import IComponentArchitecture
from zope.component.exceptions import ComponentLookupError
from zope.component.service import serviceManager
from zope.component.servicenames import Adapters, Presentation
from zope.component.servicenames import Factories

# Try to be hookable. Do so in a try/except to avoid a hard dependence
try:
    from zope.hookable import hookable
except ImportError:
    def hookable(ob):
        return ob

moduleProvides(IComponentArchitecture)
__all__ = tuple(IComponentArchitecture)

def getServiceManager(context):
    return serviceManager
getServiceManager = hookable(getServiceManager)

def getService(context, name):
    return getServiceManager(context).getService(name)

def queryService(context, name, default=None):
    sm = getServiceManager(context)
    return sm.queryService(name, default)

def getServiceDefinitions(context):
    return getServiceManager(context).getServiceDefinitions()

# Utility service

def getUtility(context, interface, name=''):
    return getService(context, 'Utilities').getUtility(interface, name)

def queryUtility(context, interface, default=None, name=''):
    return getService(context, 'Utilities').queryUtility(
        interface, default, name)

def getUtilitiesFor(context, interface):
    return getService(context, 'Utilities').getUtilitiesFor(interface)
    
# Adapter service

def getAdapter(object, interface, name='', context=None):
    adapter = queryAdapter(object, interface, None, name, context)
    if adapter is None:
        raise ComponentLookupError(object, interface)
    return adapter

def queryAdapter(object, interface, default=None, name='', context=None):
    if name:
        warnings.warn("The name argument to queryAdapter is deprecated",
                      DeprecationWarning, 2)
        return queryNamedAdapter(object, interface, name, default, context)
    
    conform = getattr(object, '__conform__', None)
    if conform is not None:
        try:
            adapter = conform(interface)
        except TypeError:
            # We got a TypeError. It might be an error raised by
            # the __conform__ implementation, or *we* may have
            # made the TypeError by calling an unbound method
            # (object is a class).  In the later case, we behave
            # as though there is no __conform__ method. We can
            # detect this case by checking whether there is more
            # than one traceback object in the traceback chain:
            if sys.exc_info()[2].tb_next is not None:
                # There is more than one entry in the chain, so
                # reraise the error:
                raise
            # This clever trick is from Phillip Eby
        else:
            if adapter is not None:
                return adapter

    if interface.providedBy(object):
        return object

    return queryNamedAdapter(object, interface, name, default, context)


def getNamedAdapter(object, interface, name, context=None):
    adapter = queryNamedAdapter(object, interface, name, context=context)
    if adapter is None:
        raise ComponentLookupError(object, interface)
    return adapter

def queryNamedAdapter(object, interface, name, default=None, context=None):
    if context is None:
        context = object
    try:
        adapters = getService(context, Adapters)
    except ComponentLookupError:
        # Oh blast, no adapter service. We're probably just running from a test
        return default

    return adapters.queryNamedAdapter(object, interface, name, default)

queryNamedAdapter = hookable(queryNamedAdapter)

def interfaceAdapterHook(iface, ob):
    try:
        adapters = getService(ob, Adapters)
    except ComponentLookupError:
        # Oh blast, no adapter service. We're probably just running from a test
        return None

    return adapters.queryNamedAdapter(ob, iface, '')

from zope.interface.interface import adapter_hooks
adapter_hooks.append(interfaceAdapterHook)

def queryMultiAdapter(objects, interface, context, name=u'', default=None):
    try:
        adapters = getService(context, Adapters)
    except ComponentLookupError:
        # Oh blast, no adapter service. We're probably just running from a test
        return default

    return adapters.queryMultiAdapter(objects, interface, name, default)

def querySubscriptionAdapter(object, interface, name, default=(),
                             context=None):
    if context is None:
        context = object
    try:
        adapters = getService(context, Adapters)
    except ComponentLookupError:
        # Oh blast, no adapter service. We're probably just running from a test
        return default

    return adapters.querySubscriptionAdapter(object, interface, name, default)

def querySubscriptionMultiAdapter(objects, interface, context, name=u'',
                             default=()):
    try:
        adapters = getService(context, Adapters)
    except ComponentLookupError:
        # Oh blast, no adapter service. We're probably just running from a test
        return default

    return adapters.querySubscriptionMultiAdapter(objects, interface, name,
                                                  default)

# Factory service

def createObject(context, name, *args, **kwargs):
    return getService(context, Factories).createObject(name, *args, **kwargs)

def getFactory(context, name):
    return getService(context, Factories).getFactory(name)

def queryFactory(context, name, default=None):
    return getService(context, Factories).queryFactory(name, default)

def getFactoryInterfaces(context, name):
    return getService(context, Factories).getInterfaces(name)


# Presentation service

def getView(object, name, request, context=None, providing=Interface):
    v = queryView(object, name, request, context=context, providing=providing)
    if v is not None:
        return v

    raise ComponentLookupError("Couldn't find view",
                               name, object, context, request)

def queryView(object, name, request,
              default=None, context=None, providing=Interface):
    if context is None:
        context = object
    s = getService(context, Presentation)
    return s.queryView(object, name, request,
                       default=default, providing=providing)

queryView = hookable(queryView)

def getDefaultViewName(object, request, context=None):
    v = queryDefaultViewName(object, request, context=context)
    if v is not None:
        return v

    raise ComponentLookupError("Couldn't find default view name",
                               context, request)

def queryDefaultViewName(object, request, default=None, context=None):
    if context is None:
        context = object
    s = getService(context, Presentation)
    return s.queryDefaultViewName(object, request, default)

def getResource(wrapped_object, name, request, providing=Interface):
    v = queryResource(wrapped_object, name, request, providing=providing)
    if v is not None:
        return v

    raise ComponentLookupError("Couldn't find resource", name, request)

def queryResource(context, name, request, default=None, providing=Interface):
    s = getService(context, Presentation)
    return s.queryResource(name, request, default, providing=providing)
