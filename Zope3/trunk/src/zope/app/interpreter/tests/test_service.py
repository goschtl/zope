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

$Id: test_service.py,v 1.2 2003/08/21 14:19:25 srichter Exp $
"""
import unittest

from zope.app.interfaces.interpreter import IInterpreter, IInterpreterService
from zope.app.interpreter import GlobalInterpreterService
from zope.interface import implements
from zope.interface.verify import verifyClass

class TestInterpreter:
    implements(IInterpreter)

TestInterpreter = TestInterpreter()

class ServiceTest(unittest.TestCase):

    def setUp(self):
        self.service = GlobalInterpreterService()
        self.service.provideInterpreter('text/server-test', TestInterpreter)

    def test_verifyInterface(self):
        self.assert_(verifyClass(IInterpreterService,
                                 GlobalInterpreterService))

    def test_getInterpreter(self):
        self.assertEqual(
            self.service.getInterpreter('text/server-test'),
            TestInterpreter)
        self.assertRaises(KeyError, self.service.getInterpreter,
                          'text/server-test2')

    def test_queryInterpreter(self):
        self.assertEqual(
            self.service.queryInterpreter('text/server-test'),
            TestInterpreter)
        self.assertEqual(
            self.service.queryInterpreter('text/server-test2', 'foo'),
            'foo')

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ServiceTest),
        ))

if __name__ == '__main__':
    unittest.main()
