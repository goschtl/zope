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
"""Interface tests

$Id: test_implements.py,v 1.3 2003/01/07 12:14:56 srichter Exp $
"""
from zope.interface import Interface
from zope.interface.implements import implements
from zope.interface.exceptions import DoesNotImplement, BrokenImplementation
from zope.interface.exceptions import BrokenMethodImplementation

import unittest, sys

class Test(unittest.TestCase):

    def testSimple(self):

        class I(Interface):
            def f(): pass

        class C: pass

        self.assertRaises(BrokenImplementation, implements, C, I)

        C.f=lambda self: None

        implements(C, I)

        self.assertEqual(C.__implements__, I)

    def testAdd(self):

        class I(Interface):
            def f(): pass

        class I2(Interface):
            def g(): pass

        class C:
            __implements__=I2

        self.assertRaises(BrokenImplementation, implements, C, I)
        self.assertRaises(BrokenImplementation, implements, C, I2)

        C.f=lambda self: None

        implements(C, I)

        self.assertEqual(C.__implements__, (I2, I))
        self.assertRaises(BrokenImplementation, implements, C, I2)

        C.g=C.f
        implements(C, I)
        implements(C, I2)


def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
