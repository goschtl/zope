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
"""Test the workflow ZCML namespace directives.

$Id: test_directives.py,v 1.2 2003/08/21 14:19:25 srichter Exp $
"""
import unittest

from zope.app.interfaces.interpreter import IInterpreter
from zope.app.interpreter import interpreterService
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.configuration import xmlconfig
from zope.interface import implements

from zope.app.interpreter import tests 

class TestInterpreter:
    implements(IInterpreter)

TestInterpreter = TestInterpreter()

class DirectivesTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        self.context = xmlconfig.file("interpreter.zcml", tests)

    def testRegisterInterpreter(self):
        self.assertEqual(
            interpreterService.getInterpreter('text/server-test'),
            TestInterpreter)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(DirectivesTest),
        ))

if __name__ == '__main__':
    unittest.main()
