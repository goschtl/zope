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

$Id: __init__.py,v 1.5 2003/02/11 16:00:04 sidnei Exp $
"""

from zope.component.interfaces import IComponentArchitecture
from zope.component.exceptions import ComponentLookupError
from zope.component.service import serviceManager
from zope.component.servicenames import Adapters, Skins, ResourceService
from zope.component.servicenames import Factories

__implements__ = IComponentArchitecture

def getServiceManager(context): # hookable
    return getServiceManager_hook(context)

def queryServiceManager(context, default=None):
    try:
        return getServiceManager(context)
    except ComponentLookupError:
        return default

def getServiceManager_hook(context): # default hook
    return serviceManager

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
    if context is None:
        context = object
    return getService(context, Adapters).getAdapter(
        object, interface, name)

def queryAdapter(object, interface, default=None, name='', context=None):
    if context is None:
        context = object
    try:
        adapters = getService(context, Adapters)
    except ComponentLookupError:
        # Oh blast, no adapter service. We're probably just running from a test
        return default

    return adapters.queryAdapter(
        object, interface, default, name)

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
                      ResourceService).getResource(
        wrapped_object, name, request)

def queryResource(wrapped_object, name, request, default=None):
    return getService(wrapped_object,
                      ResourceService).queryResource(
        wrapped_object, name, request, default)


#def _clear():
#    from Service import _clear;     _clear()
#    from ViewService import _clear; _clear()
#    from ResourceService import _clear; _clear()
#    from SkinService import _clear; _clear()
