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

$Id: test_helpdirectives.py,v 1.5 2003/08/02 11:19:25 srichter Exp $
"""
import unittest

from zope.app.interfaces.traversing import \
     ITraverser, ITraversable, IPhysicallyLocatable
from zope.app.onlinehelp import tests
from zope.app.onlinehelp import help
from zope.app.traversing.adapters import \
     Traverser, DefaultTraversable, WrapperPhysicallyLocatable
from zope.component.adapter import provideAdapter
from zope.component.tests.placelesssetup import PlacelessSetup
from zope.configuration import xmlconfig
from zope.interface import Interface


class I1(Interface):
    pass


class DirectivesTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        provideAdapter(None, ITraverser, Traverser)
        provideAdapter(None, ITraversable, DefaultTraversable)
        provideAdapter(None, IPhysicallyLocatable, WrapperPhysicallyLocatable)

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
