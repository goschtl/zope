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
"""Test the new API for making and checking interface declarations


$Id: test_declarations.py,v 1.2 2003/05/03 16:38:00 jim Exp $
"""

import unittest
from zope.interface import *
from zope.testing.doc import doctest
from zope.interface import Interface

class I1(Interface): pass
class I2(Interface): pass
class I3(Interface): pass
class I4(Interface): pass
class I5(Interface): pass

class A:
    implements(I1)
class B:
    implements(I2)
class C(A, B):
    implements(I3)

class COnly(A, B):
    implementsOnly(I3)

class COnly_old(A, B):
    __implements__ = I3
    
class D(COnly):
    implements(I5)
    

class Test(unittest.TestCase):

    # Note that most of the tests are in the doc strings of the
    # declarations module.

    def test_doctest(self):
        doctest(self, declarations)

    def test_ObjectSpecification_Simple(self):
        c = C()
        directlyProvides(c, I4)
        spec = providedBy(c)
        sig = spec.__signature__
        expect = (c.__provides__.__signature__,
                  C.__dict__['__implements__'].__signature__,
                  A.__dict__['__implements__'].__signature__,
                  B.__dict__['__implements__'].__signature__,
                  )
        self.assertEqual(sig, expect)

    def test_ObjectSpecification_Simple_w_only(self):
        c = COnly()
        directlyProvides(c, I4)
        spec = providedBy(c)
        sig = spec.__signature__
        expect = (c.__provides__.__signature__,
                  COnly.__dict__['__implements__'].__signature__,
                  A.__dict__['__implements__'].__signature__,
                  B.__dict__['__implements__'].__signature__,
                  )
        self.assertEqual(sig, expect)

    def test_ObjectSpecification_Simple_old_style(self):
        c = COnly_old()
        directlyProvides(c, I4)
        spec = providedBy(c)
        sig = spec.__signature__
        expect = (c.__provides__.__signature__,
                  COnly_old.__dict__['__implements__'].__signature__,
                  A.__dict__['__implements__'].__signature__,
                  B.__dict__['__implements__'].__signature__,
                  )
        self.assertEqual(sig, expect)

    def test_backward_compat(self):

        class C1: __implements__ = I1
        class C2(C1): __implements__ = I2, I5
        class C3(C2): __implements__ = I3, C2.__implements__

        self.assert_(C3.__implements__.__class__ is tuple)

        self.assertEqual(
            [i.__name__ for i in providedBy(C3())],
            ['I3', 'I2', 'I5'],
            )

        class C4(C3):
            implements(I4)

        self.assertEqual(
            [i.__name__ for i in providedBy(C4())],
            ['I4', 'I3', 'I2', 'I5'],
            )

        self.assertEqual(
            [i.__name__ for i in C4.__implements__],
            ['I4', 'I3', 'I2', 'I5'],
            )

        # Note that C3.__implements__ should now be a sequence of interfaces
        self.assertEqual(
            [i.__name__ for i in C3.__implements__],
            ['I3', 'I2', 'I5'],
            )
        self.failIf(C3.__implements__.__class__ is tuple)

    def test_module(self):
        import zope.interface.tests.m1
        import zope.interface.tests.m2
        directlyProvides(zope.interface.tests.m2,
                         zope.interface.tests.m1.I1,
                         zope.interface.tests.m1.I2,
                         )
        self.assertEqual(list(providedBy(zope.interface.tests.m1)),
                         list(providedBy(zope.interface.tests.m2)),
                         )

    def test_builtins(self):
        classImplements(int, I1)
        class myint(int):
            implements(I2)

        x = 42
        self.assertEqual([i.__name__ for i in providedBy(x)],
                         ['I1'])

        x = myint(42)
        directlyProvides(x, I3)
        self.assertEqual([i.__name__ for i in providedBy(x)],
                         ['I3', 'I2', 'I1'])

        # cleanup
        from zope.interface.declarations import _implements_reg
        _implements_reg.clear()

        x = 42
        self.assertEqual([i.__name__ for i in providedBy(x)],
                         [])
        


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    return suite


if __name__ == '__main__':
    unittest.main()
