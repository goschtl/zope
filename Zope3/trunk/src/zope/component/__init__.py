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

$Id$
"""
import sys
import warnings
from zope.interface import moduleProvides, Interface
from zope.interface.interfaces import IInterface
from zope.component.interfaces import IComponentArchitecture, IFactory
from zope.component.interfaces import IServiceService
from zope.component.exceptions import ComponentLookupError
from zope.component.service import serviceManager
from zope.component.servicenames import Adapters, Presentation, Utilities

# Try to be hookable. Do so in a try/except to avoid a hard dependency.
try:
    from zope.hookable import hookable
except ImportError:
    def hookable(ob):
        return ob

moduleProvides(IComponentArchitecture)
__all__ = tuple(IComponentArchitecture)

def warningLevel():
    """Returns the number of the first stack frame outside of zope.component"""
    try:
        level = 2
        while sys._getframe(level).f_globals['__name__'] == 'zope.component':
            level += 1
        return level
    except ValueError:
        return 2

def getGlobalServices():
    return serviceManager

def getServiceManager(context):
    # Backwards compatibility stub
    warnings.warn("getServiceManager(context) is  deprecated,"
                  " use getServices(context=None) instead.",
                  DeprecationWarning, 2)
    return getServices(context)


def getServices(context=None):
    if context is None:
        return serviceManager
    else:
        # Use the global service manager to adapt context to IServiceService
        # to avoid the recursion implied by using a local getAdapter call.

        # We should be using the line of code below.
        ## return getAdapter(context, IServiceService, context=None)
        #
        # Instead, we need to support code that has passed in an object
        # as context, at least until the whole component API is fixed up.
        # XXX try ripping this code out.
        sm = queryAdapter(context, IServiceService, context=None)
        if sm is None:
            # Deprecated support for a context that isn't adaptable to
            # IServiceService.  Return the default service manager.
            # warnings.warn("getServices' context arg must be None or"
            #               "  adaptable to IServiceService.",
            #               DeprecationWarning, warningLevel())
            return serviceManager
        else:
            return sm

getServices = hookable(getServices)

def getService(name, context=None):
    # Deprecated backwards-compatibility hack.
    if isinstance(context, basestring) and not isinstance(name, basestring):
        name, context = context, name
        ##warnings.warn("getService(context, name) is deprecated."
        ##              "  Use getService(name, context=context).",
        ##              DeprecationWarning, warningLevel())
    return getServices(context).getService(name)

def queryService(context, name, default=None):
    # Leaving the API in the older style of context, name, default because
    # this function is deprecated anyway.
    ##warnings.warn("queryService is deprecated.  Client code should depend"
    ##              "  on the service existing.  Use getService instead.",
    ##              DeprecationWarning, warningLevel())
    return getServices(context).queryService(name, default)

def getServiceDefinitions(context=None):
    return getServices(context).getServiceDefinitions()

# Utility service

def getUtility(interface, name='', context=None):
    if not isinstance(name, basestring):
        context, interface, name = interface, name, context
        if name is None:
            name = ''
            warnings.warn("getUtility(context, interface, name) is deprecated."
                          "  Use getUtility(interface, name, context=context).",
                          DeprecationWarning, warningLevel())
    return getService(Utilities, context=context).getUtility(interface, name)

def queryUtility(interface, default=None, name='', context=None):
    ## XXX this check is for migration.  Remove soon.
    if (not IInterface.providedBy(interface) or
        not isinstance(name, basestring)):
        raise TypeError("queryUtility got nonsense arguments."
                        " Check that you are updated with the"
                        " component API change.")
    return getService(Utilities, context).queryUtility(
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
                      DeprecationWarning, warningLevel())
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
    try:
        adapters = getService(Adapters, context)
    except ComponentLookupError:
        # Oh blast, no adapter service. We're probably just running from a test
        #warnings.warn("There is no adapters service.  Returning the default.",
        #              DeprecationWarning, warningLevel())
        return default

    return adapters.queryNamedAdapter(object, interface, name, default)

queryNamedAdapter = hookable(queryNamedAdapter)

def interfaceAdapterHook(iface, ob):
    try:
        adapters = getService(Adapters)
    except ComponentLookupError:
        # Oh blast, no adapter service. We're probably just running
        # from a test
        #warnings.warn("There is no adapters service.  Returning the default.",
        #              DeprecationWarning, warningLevel())
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
    try:
        adapters = getService(Adapters, context)
    except ComponentLookupError:
        # Oh blast, no adapter service. We're probably just running from a test
        return default

    return adapters.queryMultiAdapter(objects, interface, name, default)

def subscribers(objects, interface, context=None):
    try:
        adapters = getService(Adapters, context=context)
    except ComponentLookupError:
        # Oh blast, no adapter service. We're probably just running from a test
        return []
    return adapters.subscribers(objects, interface)


# Factories

def createObject(context, name, *args, **kwargs):
    return getUtility(IFactory, name, context)(*args, **kwargs)

def getFactoryInterfaces(name, context=None):
    return getUtility(IFactory, name, context).getInterfaces()

def getFactoriesFor(interface, context=None):
    utils = getService(Utilities, context)
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
    return getUtility(IFactory, name, context=context)

def queryFactory(context, name, default=None):
    warnings.warn(
        "Use getUtility(context, IFactory, name) instead of getFactory(...)",
        DeprecationWarning, 2)
    return queryUtility(IFactory, name=name, context=context)


# Presentation service

def getView(object, name, request, providing=Interface, context=None):
    if not IInterface.providedBy(providing):
        providing, context = context, providing
        warnings.warn("Use getView(object, name, request,"
                      " prodiving=Interface, context=Interface)"
                      " instead of getView(object, name, request,"
                      " context=None, prodiving=Interface)",
                      DeprecationWarning, 2)
    view = queryView(object, name, request, context=context,
                     providing=providing)
    if view is not None:
        return view

    raise ComponentLookupError("Couldn't find view",
                               name, object, context, request)

def queryView(object, name, request,
              default=None, providing=Interface, context=None):
    s = getService(Presentation, context=context)
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
    s = getService(Presentation, context)
    return s.queryMultiView(objects, request, providing, name, default)

def getViewProviding(object, providing, request, context=None):
    return getView(object, '', request, providing, context)

def queryViewProviding(object, providing, request, default=None, 
                       context=None):
    return queryView(object, '', request, default, providing, context)

def getDefaultViewName(object, request, context=None):
    view = queryDefaultViewName(object, request, context=context)
    if view is not None:
        return view

    raise ComponentLookupError("Couldn't find default view name",
                               context, request)

def queryDefaultViewName(object, request, default=None, context=None):
    s = getService(Presentation, context)
    return s.queryDefaultViewName(object, request, default)

def getResource(name, request, providing=Interface, context=None):
    if isinstance(request, basestring):
        # "Backwards compatibility"
        raise TypeError("getResource got incorrect arguments.")
    view = queryResource(name, request, providing=providing, context=context)
    if view is not None:
        return view

    raise ComponentLookupError("Couldn't find resource", name, request)

def queryResource(name, request, default=None, providing=Interface,
                  context=None):
    if isinstance(request, basestring):
        # "Backwards compatibility"
        raise TypeError("queryResource got incorrect arguments.")
    s = getService(Presentation, context)
    return s.queryResource(name, request, default, providing=providing)
