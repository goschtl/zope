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

Revision information:
$Id: test_type.py,v 1.2 2002/12/25 14:15:12 jim Exp $
"""

import unittest, sys
from zope.interface.type import TypeRegistry
from zope.interface import Interface

def getAllForObject(reg, ob):
    all = list(reg.getAllForObject(ob))
    all.sort()
    return all

class Test(unittest.TestCase):

    def test(self):
        class I1(Interface): pass
        class I2(I1): pass
        class I3(I2): pass

        reg = TypeRegistry()
        reg.register(I2, 2)

        class C1: __implements__ = I1
        class C2: __implements__ = I2
        class C3: __implements__ = I3
        class C: pass

        self.assertEqual(getAllForObject(reg, C1()), [])
        self.assertEqual(getAllForObject(reg, C2()), [2])
        self.assertEqual(getAllForObject(reg, C3()), [2])
        self.assertEqual(getAllForObject(reg,  C()), [])

        self.assertEqual(reg.get(I1), None)
        self.assertEqual(reg.get(I2), 2)
        self.assertEqual(reg.get(I3), None)

        reg.register(I1, 1)

        self.assertEqual(getAllForObject(reg, C1()), [1])
        self.assertEqual(getAllForObject(reg, C2()), [1, 2])
        self.assertEqual(getAllForObject(reg, C3()), [1, 2])
        self.assertEqual(getAllForObject(reg,  C()), [])

        self.assertEqual(reg.get(I1), 1)
        self.assertEqual(reg.get(I2), 2)
        self.assertEqual(reg.get(I3), None)

        reg.register(I3, 3)

        self.assertEqual(getAllForObject(reg, C1()), [1])
        self.assertEqual(getAllForObject(reg, C2()), [1, 2])
        self.assertEqual(getAllForObject(reg, C3()), [1, 2, 3])
        self.assertEqual(getAllForObject(reg,  C()), [])

        self.assertEqual(reg.get(I1), 1)
        self.assertEqual(reg.get(I2), 2)
        self.assertEqual(reg.get(I3), 3)

    def testSetdefault(self):
        class I(Interface):
            pass
        reg = TypeRegistry()
        x = reg.setdefault(I, 1)
        y = reg.setdefault(I, 2)
        self.assertEqual(x, y)
        self.assertEqual(x, 1)

    def testDup(self):
        class I1(Interface): pass
        class I2(I1): pass
        class I3(I1): pass
        class I4(I2, I3): pass
        class C1: __implements__ = I1
        class C2: __implements__ = I2
        class C3: __implements__ = I3
        class C4: __implements__ = I4
        class C5: __implements__ = I1, I2, I3, I4
        class C: pass

        reg = TypeRegistry()
        reg.register(I1, 1)
        reg.register(I2, 2)
        reg.register(I3, 3)

        self.assertEqual(getAllForObject(reg, C1()), [1])
        self.assertEqual(getAllForObject(reg, C2()), [1, 2])
        self.assertEqual(getAllForObject(reg, C3()), [1, 3])
        self.assertEqual(getAllForObject(reg, C4()), [1, 2, 3])
        self.assertEqual(getAllForObject(reg, C5()), [1, 2, 3])
        self.assertEqual(getAllForObject(reg,  C()), [])

    def testBadRequire(self):
        registry = TypeRegistry()
        self.assertRaises(TypeError, registry.register, 42, '')

def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
