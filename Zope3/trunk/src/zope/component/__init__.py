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
"""

$Id: __init__.py,v 1.9 2003/05/21 20:30:05 jim Exp $
"""

import sys
import warnings
from zope.interface import moduleProvides
from zope.component.interfaces import IComponentArchitecture
from zope.component.exceptions import ComponentLookupError
from zope.component.service import serviceManager
from zope.component.servicenames import Adapters, Skins, Resources
from zope.component.servicenames import Factories

# Try to be hookable. Do so in a try/except to avoid a hard dependence
try:
    from zope.hookable import hookable
except ImportError:
    def hookable(ob):
        return ob

moduleProvides(IComponentArchitecture)

def queryServiceManager(context, default=None):
    try:
        return getServiceManager(context)
    except ComponentLookupError:
        return default

def getServiceManager(context):
    return serviceManager
getServiceManager = hookable(getServiceManager)

def getService(context, name):
    return getServiceManager(context).getService(name)

def queryService(context, name, default=None):
    sm = queryServiceManager(context)
    if sm is None:
        return default
    return sm.queryService(name, default)

def getServiceDefinitions(context):
    return getServiceManager(context).getServiceDefinitions()

# Utility service

def getUtility(context, interface, name=''):
    return getService(context, 'Utilities').getUtility(interface, name)

def queryUtility(context, interface, default=None, name=''):
    return getService(context, 'Utilities').queryUtility(
        interface, default, name)

# Adapter service

def getAdapter(object, interface, name='', context=None):
    adapter = queryAdapter(object, interface, name=name, context=context)
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

    if interface.isImplementedBy(object):
        return object

    if context is None:
        context = object
    try:
        adapters = getService(context, Adapters)
    except ComponentLookupError:
        # Oh blast, no adapter service. We're probably just running from a test
        return default

    return adapters.queryNamedAdapter(object, interface, name, default)

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

# Factory service

def createObject(context, name, *args, **kwargs):
    return getService(context, Factories).createObject(name, *args, **kwargs)

def getFactory(context, name):
    return getService(context, Factories).getFactory(name)

def queryFactory(context, name, default=None):
    return getService(context, Factories).queryFactory(name, default)

def getFactoryInterfaces(context, name):
    return getService(context, Factories).getInterfaces(name)

# Skin service

def getSkin(wrapped_object, name, view_type):
    return getService(wrapped_object,
                      Skins).getSkin(wrapped_object, name, view_type)

# View service

def getView(wrapped_object, name, request, context=None):
    if context is None:
        context = wrapped_object
    return getService(context,
                      'Views').getView(wrapped_object, name, request)

def queryView(wrapped_object, name, request, default=None, context=None):
    if context is None:
        context = wrapped_object
    return getService(context,
                      'Views').queryView(wrapped_object, name,
                                         request, default)

def getDefaultViewName(wrapped_object, request, context=None):
    if context is None:
        context = wrapped_object
    return getService(context,
                      'Views').getDefaultViewName(wrapped_object,
                                                  request)

def queryDefaultViewName(wrapped_object, request, default=None, context=None):
    if context is None:
        context = wrapped_object
    return getService(context,
                      'Views').queryDefaultViewName(wrapped_object,
                                                    request, default)

# Resource service

def getResource(wrapped_object, name, request):
    return getService(wrapped_object,
                      Resources).getResource(
        wrapped_object, name, request)

def queryResource(wrapped_object, name, request, default=None):
    return getService(wrapped_object,
                      Resources).queryResource(
        wrapped_object, name, request, default)

