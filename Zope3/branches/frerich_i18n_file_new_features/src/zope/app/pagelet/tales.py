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
"""Pagelet tales expression registrations

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface import implements
from zope.interface import directlyProvides

from zope.tales.expressions import StringExpr

from zope.app import zapi
from zope.app.component.interface import queryInterface

from zope.app.pagelet.exceptions import PageletSlotInterfaceLookupError
from zope.app.pagelet.exceptions import \
    PageletSlotInterfaceNotProvidedException
from zope.app.pagelet.exceptions import PageletError_slot_interface_not_found
from zope.app.pagelet.exceptions import \
    PageletError_slot_interface_not_provided
from zope.app.pagelet.interfaces import ITALESPageletsExpression
from zope.app.pagelet.interfaces import ITALESPageletExpression
from zope.app.pagelet.interfaces import ITALESPageDataExpression
from zope.app.pagelet.interfaces import IPageletSlot
from zope.app.pagelet.interfaces import IPagelet
from zope.app.pagelet.interfaces import IPageData
from zope.app.pagelet.interfaces import IMacrosCollector
from zope.app.pagelet.interfaces import IMacroCollector



class Wrapper:
    """Dummy class for to provide a interface."""



class TALESPageletsExpression(StringExpr):
    """Collect pagelets via a tal namespace called tal:pagelets.

    Imports:

        >>> from zope.interface import Interface
        >>> from zope.security.checker import defineChecker
        >>> from zope.publisher.browser import TestRequest
        >>> from zope.publisher.interfaces.browser import IDefaultBrowserLayer
        >>> from zope.component.interfaces import IView
        >>> from zope.app.publisher.browser import BrowserView
        >>> from zope.app.pagelet.interfaces import IPagelet
        >>> from zope.app.pagelet.interfaces import IPageletSlot
        >>> from zope.app.pagelet.tests import TestPagelet
        >>> from zope.app.pagelet.tests import TestContext
        >>> from zope.app.pagelet.tests import testChecker

    Register pagelet:

        >>> from zope.app.testing import setup, ztapi
        >>> setup.placefulSetUp()
        >>> name = 'testpagelet'
        >>> pagelet_factory = TestPagelet
        >>> defineChecker(pagelet_factory, testChecker)
        >>> gsm = zapi.getGlobalSiteManager()
        >>> gsm.provideAdapter(
        ...        (Interface, IDefaultBrowserLayer, IView, IPageletSlot)
        ...        , IPagelet, name, pagelet_factory)

    Register slot interface:

        >>> from zope.app.component.interface import provideInterface
        >>> provideInterface('', IPageletSlot, None)

    Register pagelets collector as a adapter:

        >>> from zope.app.pagelet.collector import MacrosCollector
        >>> collector_factory = MacrosCollector
        >>> gsm.provideAdapter(
        ...        (Interface, IDefaultBrowserLayer, IView, IPageletSlot)
        ...        , IMacrosCollector, '', collector_factory)

    Register pagelets expression:

        >>> from zope.app.pagetemplate.metaconfigure import registerType
        >>> registerType('pagelets', TALESPageletsExpression)

    Setup a simply browser view called 'index' with a 'index_pagelets.pt' template:

        >>> from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
        >>> ob = TestContext()
        >>> request = TestRequest()
        >>> view = BrowserView(ob, request)
        >>> index = ViewPageTemplateFile('tests/testfiles/index_pagelets.pt')

    Call the 'index' (view) on the browser view instance:

        >>> html = index(view, request)

    Test if the pagelet content is in the html output:

        >>> import string
        >>> string.count(html, 'testpagelet macro content')
        1

    Test PageletSlotInterfaceLookupError:

        >>> no_slot_iface_index = ViewPageTemplateFile(
        ...     'tests/testfiles/index_pagelets_iface_error.pt')

        >>> try:
        ...     html = no_slot_iface_index(view, request)
        ... except PageletSlotInterfaceLookupError, e:
        ...     print e
        (u'Pagelet slot interface not found.', u'zope.interface.Interface')

    Register zope.app.interface as a utility and try again:

        >>> gsm = zapi.getGlobalSiteManager()
        >>> provideInterface('', Interface, None)
        >>> try:
        ...     html = no_slot_iface_index(view, request)
        ... except PageletSlotInterfaceNotProvidedException, e:
        ...     print e
        (u'IPageletSlot interface not provided.', u'zope.interface.Interface')

        >>> setup.placefulTearDown()

    """

    implements(ITALESPageletsExpression)

    def __call__(self, econtext):
        macros = []
        expr = self._s
        context = econtext.vars['context']
        request = econtext.vars['request']
        view = econtext.vars['view']

        # get interface from key
        slotiface = queryInterface(expr)

        # check slot
        if slotiface is None:
            raise PageletSlotInterfaceLookupError(
                    PageletError_slot_interface_not_found, expr)

        # check interface
        if not slotiface.isOrExtends(IPageletSlot):
            raise PageletSlotInterfaceNotProvidedException(
                    PageletError_slot_interface_not_provided, expr)

        slot = Wrapper()
        directlyProvides(slot, slotiface)

        collector = zapi.getMultiAdapter((context, request, view, slot)
                                        , IMacrosCollector)

        macros = collector.macros()

        return macros



class TALESPageletExpression(StringExpr):
    """Collects a single pagelet via a tal namespace called tal:pagelet.

    Imports:

        >>> import zope.component
        >>> from zope.interface import Interface
        >>> from zope.security.checker import defineChecker
        >>> from zope.publisher.browser import TestRequest
        >>> from zope.publisher.interfaces.browser import IDefaultBrowserLayer
        >>> from zope.component.interfaces import IView
        >>> from zope.app.publisher.browser import BrowserView
        >>> from zope.app.pagelet.interfaces import IPagelet
        >>> from zope.app.pagelet.interfaces import IPageletSlot
        >>> from zope.app.pagelet.tests import TestPagelet
        >>> from zope.app.pagelet.tests import TestContext
        >>> from zope.app.pagelet.tests import testChecker

    Register pagelet:

        >>> from zope.app.testing import setup, ztapi
        >>> setup.placefulSetUp()
        >>> name = 'testpagelet'
        >>> pagelet_factory = TestPagelet
        >>> defineChecker(pagelet_factory, testChecker)
        >>> gsm = zapi.getGlobalSiteManager()
        >>> gsm.provideAdapter(
        ...        (Interface, IDefaultBrowserLayer, IView, IPageletSlot)
        ...        , IPagelet, name, pagelet_factory)

    Register slot interface:

        >>> from zope.app.component.interface import provideInterface
        >>> provideInterface('', IPageletSlot, None)

    Register pagelets collector as a adapter:

        >>> from zope.app.pagelet.collector import MacroCollector
        >>> collector_factory = MacroCollector
        >>> gsm.provideAdapter(
        ...        (Interface, IDefaultBrowserLayer, IView, IPageletSlot)
        ...        , IMacroCollector, '', collector_factory)

    Register pagelets expression:

        >>> from zope.app.pagetemplate.metaconfigure import registerType
        >>> registerType('pagelet', TALESPageletExpression)

    Setup a simply browser view called 'index' with a 'index_pagelet.pt' template:

        >>> from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
        >>> ob = TestContext()
        >>> request = TestRequest()
        >>> view = BrowserView(ob, request)
        >>> index = ViewPageTemplateFile('tests/testfiles/index_pagelet.pt')

    Call the 'index' (view) on the browser view instance:

        >>> html = index(view, request)

    Test if the pagelet content is in the html output:

        >>> import string
        >>> string.count(html, 'testpagelet macro content')
        1

    Test PageletSlotInterfaceLookupError:

        >>> no_slot_iface_index = ViewPageTemplateFile(
        ...     'tests/testfiles/index_pagelet_iface_error.pt')

        >>> try:
        ...     html = no_slot_iface_index(view, request)
        ... except PageletSlotInterfaceLookupError, e:
        ...     print e
        (u'Pagelet slot interface not found.', u'zope.interface.Interface')

    Register zope.app.interface as a utility and try again:

        >>> provideInterface('', Interface, None)
        >>> try:
        ...     html = no_slot_iface_index(view, request)
        ... except PageletSlotInterfaceNotProvidedException, e:
        ...     print e
        (u'IPageletSlot interface not provided.', u'zope.interface.Interface')

        >>> setup.placefulTearDown()

    """

    implements(ITALESPageletExpression)

    def __init__(self, name, expr, engine):
        self._s = expr
        if not '/' in expr:
            error_msg = "use iface/pageletname for defining the pagelet."
            raise KeyError(error_msg)
        parts = expr.split('/')
        if len(parts) > 2:
            error_msg = "Do not use more then one / for defining iface/key"
            raise KeyError(error_msg)

        # get interface from key
        self._iface = parts[0]
        self._name = parts[1]

    def __call__(self, econtext):
        macros = []
        iface = self._iface
        name = self._name
        context = econtext.vars['context']
        request = econtext.vars['request']
        view = econtext.vars['view']

        # get interface from key
        slotiface = queryInterface(iface)

        # check slot
        if slotiface == None:
            raise PageletSlotInterfaceLookupError(
                    PageletError_slot_interface_not_found, iface)

        # check interface
        if not slotiface.isOrExtends(IPageletSlot):
            raise PageletSlotInterfaceNotProvidedException(
                    PageletError_slot_interface_not_provided, iface)

        slot = Wrapper()
        directlyProvides(slot, slotiface)

        collector = zapi.getMultiAdapter((context, request, view, slot)
                                        , IMacroCollector)

        return collector.__getitem__(name)



class TALESPageDataExpression(StringExpr):
    """Collect page data adapters via a tal namespace called tal:pagedata.

    Imports:

        >>> import zope.component
        >>> from zope.interface import Interface
        >>> from zope.security.checker import defineChecker
        >>> from zope.publisher.browser import TestRequest
        >>> from zope.publisher.interfaces.browser import IDefaultBrowserLayer
        >>> from zope.component.interfaces import IView
        >>> from zope.app.publisher.browser import BrowserView
        >>> from zope.app.pagelet.interfaces import IPageletSlot
        >>> from zope.app.pagelet.tests import TestContext
        >>> from zope.app.pagelet.tests import TestClass
        >>> from zope.app.pagelet.tests import testChecker

    Register pagedata class:

        >>> from zope.app.testing import setup, ztapi
        >>> setup.placefulSetUp()
        >>> factory = TestClass
        >>> defineChecker(factory, testChecker)
        >>> gsm = zapi.getGlobalSiteManager()
        >>> gsm.provideAdapter(
        ...        (Interface, IDefaultBrowserLayer, IView)
        ...        , IPageData, '', factory)

    Register slot interface:

        >>> from zope.app.component.interface import provideInterface
        >>> provideInterface('', IPageData, None)

    Register pagelets collector as a adapter:

        >>> from zope.app.pagelet.collector import MacroCollector
        >>> collector_factory = MacroCollector
        >>> gsm.provideAdapter(
        ...        (Interface, IDefaultBrowserLayer, IView, IPageletSlot)
        ...        , IMacroCollector, '', collector_factory)

    Register pagedata expression:

        >>> from zope.app.pagetemplate.metaconfigure import registerType
        >>> registerType('pagedata', TALESPageDataExpression)

    Setup a simply browser view called 'index' with a 'index_pagedata.pt' template:

        >>> from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
        >>> ob = TestContext()
        >>> request = TestRequest()
        >>> view = BrowserView(ob, request)
        >>> index = ViewPageTemplateFile('tests/testfiles/index_pagedata.pt')

    Call the 'index' (view) on the browser view instance:

        >>> html = index(view, request)

    Test if the pagelet content is in the html output:

        >>> import string
        >>> string.count(html, 'A demo string.')
        1

    """

    implements(ITALESPageDataExpression)

    def __init__(self, name, expr, engine):
        if '/' in expr:
            # named adapter
            parts = expr.split('/')
            self._iface = parts[0]
            self._name = parts[1]

        else:
            # unnamed adapter
            self._iface = expr
            self._name = ''

    def __call__(self, econtext):
        macros = []
        iface = self._iface
        name = self._name
        context = econtext.vars['context']
        request = econtext.vars['request']
        view = econtext.vars['view']

        # get interface from key
        iface = queryInterface(iface)

        # check slot
        if iface == None:
            raise PageletSlotInterfaceLookupError(
                    PageletError_slot_interface_not_found, iface)

        # check interface
        if not iface.isOrExtends(IPageData):
            raise PageletSlotInterfaceNotProvidedException(
                    PageletError_slot_interface_not_provided, iface)

        # get a page data adapter registred on context, request, view
        pagedata = zapi.getMultiAdapter((context, request, view)
                                       , iface, name)

        return pagedata
