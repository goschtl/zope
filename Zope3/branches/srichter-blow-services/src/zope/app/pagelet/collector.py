##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Pagelet collectors

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface import implements
from zope.interface import directlyProvides

from zope.app import zapi

from zope.app.pagelet.interfaces import IPagelet
from zope.app.pagelet.interfaces import IMacrosCollector
from zope.app.pagelet.interfaces import IMacroCollector



class MacrosCollector(object):
    """Replaceable sample implementation of IMacrosCollector.
    
    Collects pagelets from the site manager.
    Pagelet adapters are registred on context, request, view and slot
    interfaces. Use your own IMacrosCollector implementation for
    to support a layout manager.

    Imports:
    
        >>> from zope.interface import Interface
        >>> from zope.publisher.browser import TestRequest
        >>> from zope.publisher.interfaces.browser import IBrowserRequest
        >>> from zope.component.interfaces import IView
        >>> from zope.app.publisher.browser import BrowserView
        >>> from zope.app.pagelet.interfaces import IPagelet
        >>> from zope.app.pagelet.interfaces import IPageletSlot
        >>> from zope.app.pagelet.tests import TestPagelet
        >>> from zope.app.pagelet.tests import TestContext
        >>> from zope.app.pagelet.tests import TestSlot

    Setup pagelet:

        >>> ob = TestContext()
        >>> name = 'testpagelet'
        >>> factory = TestPagelet

    Register the pagelet class as a factory on the site manager:

        >>> from zope.app.testing import placelesssetup, ztapi
        >>> placelesssetup.setUp()
        >>> gsm = zapi.getGlobalSiteManager()
        >>> gsm.provideAdapter(
        ...        (Interface, IBrowserRequest, IView, IPageletSlot)
        ...        , IPagelet, name, factory)

    Setup macros collector:
        
        >>> request = TestRequest()
        >>> view = BrowserView(ob, request)
        >>> slot = TestSlot()
        >>> collector = MacrosCollector(ob, request, view, slot)

    Get macros form the collector

        >>> macros = collector.macros()

    Test if we have the string form the test_pagelet in the macro:

        >>> rawtextOffset = macros[0][5][1][0]
        >>> rawtextOffset
        'testpagelet macro content</div>'

      >>> placelesssetup.tearDown()

    """

    implements(IMacrosCollector)

    def __init__ (self, context, request, view, slot):
        self.context = context
        self.request = request
        self.view = view
        self.slot = slot
        
    def macros(self):
        macros = []

        # collect pagelets
        objects = self.context, self.request, self.view, self.slot
        adapters = zapi.getAdapters(objects, IPagelet)
        adapters.sort(lambda x, y: x[1].weight - y[1].weight)

        for name, pagelet in adapters:
            # append pagelet macros 
            macros.append(pagelet[name])
            
        return macros



class MacroCollector(object):
    """Replaceable sample implementation of IMacroCollector.
    
    Collect a single pagelet from the adapter service and returns 
    a macro by name.
    Pagelet adapters are registred on context, request, view and slot
    interfaces. Use your own IMacroCollector implementation for
    to support a layout manager which can return a macro dependent
    on additional rules.


    Imports:
    
        >>> from zope.interface import Interface
        >>> from zope.publisher.browser import TestRequest
        >>> from zope.publisher.interfaces.browser import IBrowserRequest
        >>> from zope.component.interfaces import IView
        >>> from zope.app.publisher.browser import BrowserView
        >>> from zope.app.pagelet.interfaces import IPagelet
        >>> from zope.app.pagelet.interfaces import IPageletSlot
        >>> from zope.app.pagelet.tests import TestPagelet
        >>> from zope.app.pagelet.tests import TestContext
        >>> from zope.app.pagelet.tests import TestSlot

    Setup pagelet:

        >>> ob = TestContext()
        >>> name = 'testpagelet'
        >>> factory = TestPagelet

    Register the pagelet class as a factory on the site manager:

        >>> from zope.app.testing import placelesssetup, ztapi
        >>> placelesssetup.setUp()
        >>> gsm = zapi.getGlobalSiteManager()
        >>> gsm.provideAdapter(
        ...        (Interface, IBrowserRequest, IView, IPageletSlot)
        ...        , IPagelet, name, factory)

    Setup macros collector:
        
        >>> request = TestRequest()
        >>> view = BrowserView(ob, request)
        >>> slot = TestSlot()
        >>> collector = MacroCollector(ob, request, view, slot)

    Get the macro form the collector

        >>> macro = collector.__getitem__('testpagelet')

    Test if we have the string form the test_pagelet.pt file in the macro:

        >>> rawtextOffset = macro[5][1][0]
        >>> rawtextOffset
        'testpagelet macro content</div>'

      >>> placelesssetup.tearDown()

    """

    implements(IMacroCollector)

    def __init__ (self, context, request, view, slot):
        self.context = context
        self.request = request
        self.view = view
        self.slot = slot
        
    def __getitem__(self, key):
        macros = []

        # collect a single pagelet which is a pagelet
        objects = self.context, self.request, self.view, self.slot
        adapter = zapi.getMultiAdapter(objects, IPagelet, key)
            
        return adapter[key]

