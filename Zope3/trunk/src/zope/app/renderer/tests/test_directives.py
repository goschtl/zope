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
"""Test the wiki ZCML namespace directives.

$Id: test_directives.py,v 1.1 2003/07/31 17:59:41 srichter Exp $
"""
import os
import unittest

from cStringIO import StringIO

from zope.interface import Interface, implements
from zope.component import getView
from zope.component.tests.placelesssetup import PlacelessSetup
from zope.configuration import xmlconfig, tests
from zope.publisher.browser import BrowserView, TestRequest

import zope.app.renderer
from zope.app.renderer.sourcetype import SourceTypes


class ITestSource(Interface):
    pass

class TestSource(unicode):
    implements(ITestSource)
    

class TestRenderer(BrowserView):
    __used_for__ = ITestSource


class DirectivesTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        self.context = xmlconfig.file("simple.zcml", tests)

    def test_sourcetype(self):
        self.assertEqual(SourceTypes.getAllTitles(), [])
        self.context = xmlconfig.file("tests/renderer.zcml", zope.app.renderer)
        self.assertEqual(SourceTypes.getAllTitles(), ['Test Text'])
        self.assertEqual(
            SourceTypes.get('Test Text'),
            zope.app.renderer.tests.test_directives.ITestSource)
        
        obj = SourceTypes.createObject('Test Text', 'Source')
        self.assertEqual(
            getView(obj, None, TestRequest()).__class__,
            zope.app.renderer.tests.test_directives.TestRenderer)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(DirectivesTest),
        ))

if __name__ == '__main__':
    unittest.main()
