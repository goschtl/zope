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
"""Test the gts ZCML namespace directives.

$Id$
"""
import unittest

from zope.app.traversing.interfaces import IPhysicallyLocatable
from zope.app.traversing.interfaces import ITraverser, ITraversable
from zope.app.onlinehelp import tests
from zope.app.onlinehelp import help
from zope.app.location.traversing import LocationPhysicallyLocatable
from zope.app.traversing.adapters import Traverser, DefaultTraversable
from zope.app.tests import ztapi
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.configuration import xmlconfig
from zope.interface import Interface


class I1(Interface):
    pass


class DirectivesTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(DirectivesTest, self).setUp()
        ztapi.provideAdapter(None, ITraverser, Traverser)
        ztapi.provideAdapter(None, ITraversable, DefaultTraversable)
        ztapi.provideAdapter(None, IPhysicallyLocatable,
                             LocationPhysicallyLocatable)

    def test_register(self):
        self.assertEqual(help.keys(), [])
        self.context = xmlconfig.file("help.zcml", tests)
        self.assertEqual(help.keys(), ['help1'])
        topic = help['help1']
        self.assert_('test1.png' in topic.keys())

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(DirectivesTest),
        ))

if __name__ == '__main__':
    unittest.main()
