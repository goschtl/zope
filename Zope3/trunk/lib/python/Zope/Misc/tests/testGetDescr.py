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
"""
Test GetDescr.

Revision information:
$Id: testGetDescr.py,v 1.2 2002/06/10 23:29:29 jim Exp $
"""

import unittest
from Zope.Misc.GetDescr import GetDescr

class TestGetDescr(unittest.TestCase):

    def test_errors(self):
        class C: pass
        # obj not a new-style instance
        self.assertRaises(TypeError, GetDescr, C(), "foo")
        # name not a string
        self.assertRaises(TypeError, GetDescr, 0, 0)

    def test_simple(self):
        # Simple cases
        class C(object):
            def foo(self): pass
        c = C()
        self.assertEqual(GetDescr(c, "foo"), C.__dict__["foo"])
        self.assertEqual(GetDescr(c, "bar"), None)
        c.bar = 12
        self.assertEqual(GetDescr(c, "bar"), None)
        c.foo = 12
        self.assertEqual(GetDescr(c, "foo"), None)
        # Make sure method overrides overrid
        class D(C):
            def foo(self): pass
        d = D()
        self.assertEqual(GetDescr(d, "foo"), D.__dict__["foo"])
        # Make sure properties always win
        class E(C):
            foo = property(lambda self: 42, lambda self, value: None)
        e = E()
        self.assertEqual(GetDescr(e, "foo"), E.__dict__["foo"])
        e.foo = 12 # Ignored
        self.assertEqual(e.foo, 42)
        self.assertEqual(GetDescr(e, "foo"), E.__dict__["foo"])
        e.__dict__["foo"] = 23 # Still ignored!
        self.assertEqual(e.foo, 42)
        self.assertEqual(GetDescr(e, "foo"), E.__dict__["foo"])

def test_suite():
    return unittest.makeSuite(TestGetDescr)

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
