##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
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
from zope.interface import moduleProvides, Interface, providedBy
from zope.component.interfaces import IComponentArchitecture
from zope.component.interfaces import IDefaultViewName
from zope.component.interfaces import IFactory
from zope.component.interfaces import ISiteManager
from zope.component.interfaces import ComponentLookupError
from zope.component.site import globalSiteManager

##############################################################################
# BBB: Import some backward-compatibility; 12/10/2004
from zope.component.bbb import exceptions
sys.modules['zope.component.exceptions'] = exceptions
from zope.component.bbb import service
sys.modules['zope.component.service'] = service
from zope.component.bbb import adapter
sys.modules['zope.component.adapter'] = adapter
from zope.component.bbb import utility
sys.modules['zope.component.utility'] = utility
from zope.component.bbb import servicenames
sys.modules['zope.component.servicenames'] = servicenames
from zope.component.bbb import contextdependent
sys.modules['zope.component.contextdependent'] = contextdependent

from zope.component.bbb.tests import placelesssetup
sys.modules['zope.component.tests.placelesssetup'] = placelesssetup
from zope.component.bbb.tests import request
sys.modules['zope.component.tests.request'] = request
from zope.component.bbb.tests import components
sys.modules['zope.component.tests.components'] = components


service.__warn__ = False
service.serviceManager = service.GlobalServiceManager(
    'serviceManager', __name__, globalSiteManager)
service.__warn__ = True

from zope.component.bbb import getGlobalServices, getGlobalService
from zope.component.bbb import getServices, getService
from zope.component.bbb import getServiceDefinitions
from zope.component.bbb import getView, queryView
from zope.component.bbb import getMultiView, queryMultiView
from zope.component.bbb import getViewProviding, queryViewProviding
from zope.component.bbb import getDefaultViewName, queryDefaultViewName
from zope.component.bbb import getResource, queryResource
##############################################################################


# Try to be hookable. Do so in a try/except to avoid a hard dependency.
try:
    from zope.hookable import hookable
except ImportError:
    def hookable(ob):
        return ob

moduleProvides(IComponentArchitecture)
__all__ = tuple(IComponentArchitecture)

# SiteManager API

def getGlobalSiteManager():
    return globalSiteManager

def getSiteManager(context=None):
    if context is None:
        return getGlobalSiteManager()
    else:
        # Use the global site manager to adapt context to `ISiteManager`
        # to avoid the recursion implied by using a local `getAdapter()` call.
        try:
            return ISiteManager(context)
        except TypeError, error:
            raise ComponentLookupError(*error.args)

getSiteManager = hookable(getSiteManager)


# Adapter API

def getAdapterInContext(object, interface, context):
    adapter = queryAdapterInContext(object, interface, context)
    if adapter is None:
        raise ComponentLookupError(object, interface)
    return adapter

def queryAdapterInContext(object, interface, context, default=None):
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

    return getSiteManager(context).queryAdapter(object, interface, '', default)

def getAdapter(object, interface, name, context=None):
    adapter = queryAdapter(object, interface, name, None, context)
    if adapter is None:
        raise ComponentLookupError(object, interface)
    return adapter

def queryAdapter(object, interface, name, default=None, context=None):
    if context is None:
        return adapter_hook(interface, object, name, default)
    return getSiteManager(context).queryAdapter(object, interface, name,
                                                default)

def getMultiAdapter(objects, interface, name=u'', context=None):
    adapter = queryMultiAdapter(objects, interface, name, context=context)
    if adapter is None:
        raise ComponentLookupError(objects, interface)
    return adapter

def queryMultiAdapter(objects, interface, name=u'', default=None,
                      context=None):
    try:
        sitemanager = getSiteManager(context)
    except ComponentLookupError:
        # Oh blast, no site manager. This should *never* happen!
        return default

    return sitemanager.queryMultiAdapter(objects, interface, name, default)

def getAdapters(objects, provided, context=None):
    try:
        sitemanager = getSiteManager(context)
    except ComponentLookupError:
        # Oh blast, no site manager. This should *never* happen!
        return []
    return sitemanager.getAdapters(objects, provided)


def subscribers(objects, interface, context=None):
    try:
        sitemanager = getSiteManager(context)
    except ComponentLookupError:
        # Oh blast, no site manager. This should *never* happen!
        return []
    return sitemanager.subscribers(objects, interface)

#############################################################################
# Register the component architectures adapter hook, with the adapter hook
# registry of the `zope.inteface` package. This way we will be able to call
# interfaces to create adapters for objects. For example, `I1(ob)` is
# equvalent to `getAdapterInContext(I1, ob, '')`.
def adapter_hook(interface, object, name='', default=None):
    try:
        sitemanager = getSiteManager()
    except ComponentLookupError:
        # Oh blast, no site manager. This should *never* happen!
        return None
    return sitemanager.queryAdapter(object, interface, name, default)

# Make the component architecture's adapter hook hookable 
adapter_hook = hookable(adapter_hook)

import zope.interface.interface
zope.interface.interface.adapter_hooks.append(adapter_hook)
#############################################################################


# Utility API

def getUtility(interface, name='', context=None):
    utility = queryUtility(interface, name, context=context)
    if utility is not None:
        return utility
    raise ComponentLookupError(interface, name)

def queryUtility(interface, name='', default=None, context=None):
    return getSiteManager(context).queryUtility(interface, name, default)

def getUtilitiesFor(interface, context=None):
    return getSiteManager(context).getUtilitiesFor(interface)


def getAllUtilitiesRegisteredFor(interface, context=None):
    return getSiteManager(context).getAllUtilitiesRegisteredFor(interface)


# Factories

def createObject(context, name, *args, **kwargs):
    return getUtility(IFactory, name, context)(*args, **kwargs)

def getFactoryInterfaces(name, context=None):
    return getUtility(IFactory, name, context).getInterfaces()

def getFactoriesFor(interface, context=None):
    utils = getSiteManager(context)
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
