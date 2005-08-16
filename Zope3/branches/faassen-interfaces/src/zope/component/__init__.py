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

$Id: __init__.py,v 1.31 2004/04/24 23:20:34 srichter Exp $
"""
import sys
import warnings
from zope.interface import moduleProvides, Interface
from zope.component.interfaces import IComponentArchitecture, IFactory
from zope.component.exceptions import ComponentLookupError
from zope.component.service import serviceManager
from zope.component.servicenames import Adapters, Presentation, Utilities

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
    return getService(context, Utilities).getUtility(interface, name)

def queryUtility(context, interface, default=None, name=''):
    return getService(context, Utilities).queryUtility(
        interface, default, name)

def getUtilitiesFor(context, interface):
    return getService(context, Utilities).getUtilitiesFor(interface)

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

        # Oh blast, no adapter service. We're probably just running
        # from a test

        return None

    return adapters.queryNamedAdapter(ob, iface, '')

from zope.interface.interface import adapter_hooks
adapter_hooks.append(interfaceAdapterHook)


def getMultiAdapter(objects, interface, name=u'', context=None):
    adapter = queryMultiAdapter(objects, interface, name, context=context)
    if adapter is None:
        raise ComponentLookupError(objects, interface)
    return adapter

def queryMultiAdapter(objects, interface, name=u'', default=None,
                      context=None):
    if context is None and objects:
        context = objects[0]

    try:
        adapters = getService(context, Adapters)
    except ComponentLookupError:
        # Oh blast, no adapter service. We're probably just running from a test
        return default

    return adapters.queryMultiAdapter(objects, interface, name, default)

def subscribers(objects, interface, context=None):
    if context is None and objects:
        context = objects[0]
    try:
        adapters = getService(context, Adapters)
    except ComponentLookupError:
        # Oh blast, no adapter service. We're probably just running from a test
        return []
    return adapters.subscribers(objects, interface)


# Factories

def createObject(context, name, *args, **kwargs):
    return getUtility(context, IFactory, name)(*args, **kwargs)

def getFactoryInterfaces(context, name):
    return getUtility(context, IFactory, name).getInterfaces()

def getFactoriesFor(context, interface):
    utils = getService(context, Utilities)
    for (name, factory) in utils.getUtilitiesFor(IFactory):
        interfaces = factory.getInterfaces()
        try:
            if interfaces.isOrExtends(interface):
                yield name, factory
        except AttributeError:
            for iface in interfaces:
                if iface.isOrExtends(interface):
                    yield name, factory
                    break

def getFactory(context, name):
    warnings.warn(
        "Use getUtility(context, IFactory, name) instead of getFactory(...)",
        DeprecationWarning, 2)
    return getUtility(context, IFactory, name)

def queryFactory(context, name, default=None):
    warnings.warn(
        "Use getUtility(context, IFactory, name) instead of getFactory(...)",
        DeprecationWarning, 2)
    return queryUtility(context, IFactory, name=name)


# Presentation service

def getView(object, name, request, context=None, providing=Interface):
    view = queryView(object, name, request, context=context,
                     providing=providing)
    if view is not None:
        return view

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

def getMultiView(objects, request, providing=Interface, name='', context=None):
    view = queryMultiView(objects, request, providing, name, context=context)
    if view is not None:
        return view

    raise ComponentLookupError("Couldn't find view",
                               name, object, context, request)

def queryMultiView(objects, request, providing=Interface, name='',
                   default=None, context=None):
    if context is None:
        context = objects[0]
    s = getService(context, Presentation)
    return s.queryMultiView(objects, request, providing, name, default)

def getViewProviding(object, providing, request, context=None):
    return getView(object, '', request, context, providing)

def queryViewProviding(object, providing, request, default=None, 
                       context=None):
    return queryView(object, '', request, default, context, providing)

def getDefaultViewName(object, request, context=None):
    view = queryDefaultViewName(object, request, context=context)
    if view is not None:
        return view

    raise ComponentLookupError("Couldn't find default view name",
                               context, request)

def queryDefaultViewName(object, request, default=None, context=None):
    if context is None:
        context = object
    s = getService(context, Presentation)
    return s.queryDefaultViewName(object, request, default)

def getResource(wrapped_object, name, request, providing=Interface):
    view = queryResource(wrapped_object, name, request, providing=providing)
    if view is not None:
        return view

    raise ComponentLookupError("Couldn't find resource", name, request)

def queryResource(context, name, request, default=None, providing=Interface):
    s = getService(context, Presentation)
    return s.queryResource(name, request, default, providing=providing)
