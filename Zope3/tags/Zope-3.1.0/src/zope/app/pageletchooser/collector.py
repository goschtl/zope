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
"""PageletChooser collector

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface import implements
from zope.security import canAccess
from zope.security.interfaces import Unauthorized

from zope.app import zapi
from zope.app.pagelet.interfaces import IPagelet
from zope.app.pagelet.collector import MacroCollector
from zope.app.pageletchooser.interfaces import IMacroChooser
from zope.app.pageletchooser.interfaces import IPageletNameManager



class MacroChooser(MacroCollector):
    """Returns the macro by name.

        For to get the macro name, the adapter IPageletNameManager is 
        calling the mapped name under the given key via getattr. This
        means the adapted object has to support a field property with
        the given key and has to return a existing pagelet macro name.

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
        >>> from zope.app.pagelet.tests import TestSlot
        >>> from zope.app.pagelet.tests import testChecker
        >>> from zope.app.pageletchooser.tests import TestMapping

    Setup pagelet:

        >>> ob = TestContext()
        >>> name = 'testpagelet'
        >>> factory = TestPagelet

    Register the pagelet class as a factory on the site manager:

        >>> from zope.app.testing import placelesssetup, ztapi
        >>> placelesssetup.setUp()
        >>> defineChecker(factory, testChecker)
        >>> gsm = zapi.getGlobalSiteManager()
        >>> gsm.provideAdapter(
        ...        (Interface, IDefaultBrowserLayer, IView, IPageletSlot)
        ...        , IPagelet, name, factory)

    Setup macro chooser:

        >>> request = TestRequest()
        >>> view = BrowserView(ob, request)
        >>> slot = TestSlot()
        >>> chooser = MacroChooser(ob, request, view, slot)

    Setup the IPageletNameManager adapter

        >>> ztapi.provideAdapter(Interface, IPageletNameManager
        ...                     ,TestMapping)

    Get the macro form the MacroChooser

        >>> macro = chooser.__getitem__('alias')

    Test if we have the string form the test_pagelet.pt file in the macro:

        >>> rawtextOffset = macro[5][1][0]
        >>> rawtextOffset
        u'testpagelet macro content</div>'

      >>> placelesssetup.tearDown()

    """

    implements(IMacroChooser)

    _defaultmacroname = 'notfoundmacro'

    def __getitem__(self, key):
        adapter = IPageletNameManager(self.context)
        try:
            macroname = getattr(adapter, key)
        except:
            macroname = self._defaultmacroname

        objects = self.context, self.request, self.view, self.slot
        pagelet = zapi.getMultiAdapter(objects, IPagelet, macroname)

        # rasie Unauthorized exception if we don't have the permission for 
        # calling the pagelet's macro code
        if canAccess(pagelet, '__getitem__'):
                return pagelet[macroname]
        else:
            raise Unauthorized(key)
