##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Testing helper functions

$Id: ztapi.py,v 1.3 2003/12/05 12:41:38 philikon Exp $
"""
from zope.app import zapi
import zope.interface
from zope.component.servicenames import Presentation, Adapters, Utilities
from zope.publisher.browser import IBrowserRequest

def browserView(for_, name, factory, layer='default'):
    """Define a global browser view
    """
    s = zapi.getService(None, Presentation)
    return s.provideView(for_, name, IBrowserRequest, factory, layer)

def browserResource(name, factory, layer='default'):
    """Define a global browser view
    """
    s = zapi.getService(None, Presentation)
    return s.provideResource(name, IBrowserRequest, factory, layer)

def setDefaultViewName(for_, name, layer='default'):
    s = zapi.getService(None, Presentation)
    s.setDefaultViewName(for_, IBrowserRequest, name, layer=layer)

stypes = list, tuple
def provideAdapter(required, provided, factory, name='', with=()):
    s = zapi.getService(None, Adapters)
    if not isinstance(factory, stypes):
        factory = [factory]
    s.provideAdapter(required, provided, factory, name, with)
    
def provideUtility(provided, component, name=''):
    s = zapi.getService(None, Utilities)
    s.provideUtility(provided, component, name)
