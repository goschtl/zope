##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: test_ContextAware.py,v 1.1 2003/01/25 15:32:52 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.proxy.context import ContextAware, ContextWrapper
from zope.proxy.context import getWrapperContainer

def setter(self, v):
    self.v = getWrapperContainer(self), v

class B(object):

    p1B = property(getWrapperContainer)

    p2B = property(getWrapperContainer,
                   setter)

    def fB(self):
        return getWrapperContainer(self)

class C(B, ContextAware):

    p1C = property(getWrapperContainer)

    p2C = property(getWrapperContainer,
                   setter)

    def fC(self):
        return getWrapperContainer(self)
        

class Test(TestCase):

    def test(self):

        # Reality check no context case:
        b = B()
        self.assertEqual(b.p1B, None)
        self.assertEqual(b.p2B, None)
        self.assertEqual(b.fB(), None)
        b.p2B = 1
        self.assertEqual(b.v, (None, 1))

        # Reality check no wrapper case:
        b = C()
        self.assertEqual(b.p1B, None)
        self.assertEqual(b.p2B, None)
        self.assertEqual(b.fB(), None)
        b.p2B = 1
        self.assertEqual(b.v, (None, 1))

        self.assertEqual(b.p1C, None)
        self.assertEqual(b.p2C, None)
        self.assertEqual(b.fC(), None)
        b.p2C = 1
        self.assertEqual(b.v, (None, 1))
        
        # Check wrapper case
        b = ContextWrapper(b, 42)
        self.assertEqual(b.p1B, 42)
        self.assertEqual(b.p2B, 42)
        self.assertEqual(b.fB(), 42)
        b.p2B = 1
        self.assertEqual(b.v, (42, 1))

        self.assertEqual(b.p1C, 42)
        self.assertEqual(b.p2C, 42)
        self.assertEqual(b.fC(), 42)
        b.p2C = 2
        self.assertEqual(b.v, (42, 2))

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
