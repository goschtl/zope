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
"""Pagelet tests

$Id$
"""
__docformat__ = 'restructuredtext'

import unittest

from zope.configuration import xmlconfig

from zope.publisher.browser import TestRequest

from zope.interface import directlyProvides

from zope.security.proxy import removeSecurityProxy

from zope.component.tests.placelesssetup import PlacelessSetup
from zope.component.interfaces import IView

from zope.app import zapi
from zope.app.servicenames import Adapters
from zope.app.component.interface import queryInterface

from zope.app.pagelet.interfaces import IPagelet
from zope.app.pagelet import tests



class Wrapper:
    """Dummy class for to provide some interface."""


class PageletDirectiveTest(PlacelessSetup, unittest.TestCase):
    """Pagelet directive test."""

    def setUp (self):
        PlacelessSetup.setUp(self)
        self.context = xmlconfig.file("pagelets.zcml", tests)

    def test_pagelets (self):
        key = 'zope.app.pagelet.tests.ITestSlot'
        slot = queryInterface(key)
        context = removeSecurityProxy(self.context)
        slotwrapper = Wrapper()
        viewwrapper = Wrapper()
        directlyProvides(slotwrapper, slot)
        directlyProvides(viewwrapper, IView)
        objects = context, TestRequest(), viewwrapper, slotwrapper
        views = zapi.getAdapters(objects, IPagelet)
        self.assertEqual(len(views), 1)
        self.assertEqual(views[0][0], u'testpagelet')

        
def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(PageletDirectiveTest),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
