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
"""Test the gts ZCML namespace directives.

$Id: test_helpdirectives.py,v 1.7 2003/11/21 17:12:08 jim Exp $
"""
import unittest

from zope.app.interfaces.traversing import IPhysicallyLocatable
from zope.app.interfaces.traversing import ITraverser, ITraversable
from zope.app.onlinehelp import tests
from zope.app.onlinehelp import help
from zope.app.location import LocationPhysicallyLocatable
from zope.app.traversing.adapters import Traverser, DefaultTraversable
from zope.app.tests import ztapi
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.configuration import xmlconfig
from zope.interface import Interface


class I1(Interface):
    pass


class DirectivesTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        ztapi.provideAdapter(None, ITraverser, Traverser)
        ztapi.provideAdapter(None, ITraversable, DefaultTraversable)
        ztapi.provideAdapter(None, IPhysicallyLocatable,
                             LocationPhysicallyLocatable)

    def test_register(self):
        self.assertEqual(help.keys(), [])
        self.context = xmlconfig.file("help.zcml", tests)
        self.assertEqual(help.keys(), ['help1'])
        self.assertEqual(help._registry[(I1, 'view.html')][0].title, 'Help')


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(DirectivesTest),
        ))

if __name__ == '__main__':
    unittest.main()
