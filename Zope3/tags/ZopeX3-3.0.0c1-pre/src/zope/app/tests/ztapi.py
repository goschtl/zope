##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Testing helper functions

$Id$
"""
from zope.app import zapi
import zope.interface
from zope.component.servicenames import Presentation, Adapters, Utilities
from zope.publisher.browser import IBrowserRequest
from zope.app.traversing.interfaces import ITraversable

def provideView(for_, type, providing, name, factory, layer="default"):
    s = zapi.getGlobalServices().getService(Presentation)
    return s.provideView(for_, name, type, factory, layer,
                         providing=providing)
    

def browserView(for_, name, factory, layer='default',
                providing=zope.interface.Interface):
    """Define a global browser view
    """
    if isinstance(factory, (list, tuple)):
        raise ValueError("Factory cannot be a list or tuple")
    s = zapi.getGlobalServices().getService(Presentation)
    return s.provideView(for_, name, IBrowserRequest, factory, layer,
                         providing=providing)

def browserViewProviding(for_, factory, providing, layer='default'):
    """Define a view providing a particular interface."""
    if isinstance(factory, (list, tuple)):
        raise ValueError("Factory cannot be a list or tuple")
    return browserView(for_, '', factory, layer, providing)

def browserResource(name, factory, layer='default',
                    providing=zope.interface.Interface):
    """Define a global browser view
    """
    if isinstance(factory, (list, tuple)):
        raise ValueError("Factory cannot be a list or tuple")
    s = zapi.getGlobalServices().getService(Presentation)
    return s.provideResource(name, IBrowserRequest, factory, layer,
                             providing=providing)

def setDefaultViewName(for_, name, layer='default'):
    s = zapi.getGlobalServices().getService(Presentation)
    s.setDefaultViewName(for_, IBrowserRequest, name, layer=layer)

stypes = list, tuple
def provideAdapter(required, provided, factory, name='', with=()):
    if isinstance(factory, (list, tuple)):
        raise ValueError("Factory cannot be a list or tuple")
    s = zapi.getGlobalServices().getService(Adapters)

    if with:
        required = (required, ) + tuple(with)
    elif not isinstance(required, stypes):
        required = [required]

    s.register(required, provided, name, factory)

def subscribe(required, provided, factory):
    s = zapi.getGlobalServices().getService(Adapters)
    s.subscribe(required, provided, factory)

def handle(required, handler):
    subscribe(required, None, handler)

def provideUtility(provided, component, name=''):
    s = zapi.getGlobalServices().getService(Utilities)
    s.provideUtility(provided, component, name)

def unprovideUtility(provided, name=''):
    s = zapi.getGlobalServices().getService(Utilities)
    s.register((), provided, name, None)

def provideNamespaceHandler(name, handler):
    provideAdapter(None, ITraversable, handler, name=name)
    provideView(None, None, ITraversable, name, handler)
