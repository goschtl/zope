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

$Id: testSimpleRegistry.py,v 1.2 2002/06/10 23:27:50 jim Exp $
"""

import unittest
from Interface import Interface
from Zope.App.Formulator.SimpleRegistry import SimpleRegistry, \
     ZopeDuplicateRegistryEntryError, ZopeIllegalInterfaceError


class I1(Interface):
    pass


class I2(Interface):
    pass


class Object1:
    __implements__ = I1


class Object2:
    __implements__ = I2


class Test( unittest.TestCase ):


    def testRegister(self):

        registry = SimpleRegistry(I1)
        obj1 = Object1()

        self.assertEqual(registry.objects, {})
        
        registry.register('obj1', obj1)
        self.assertEqual(registry.objects, {'obj1': obj1})

        registry.register('obj2', obj1)
        self.assertEqual(registry.objects, {'obj1': obj1, 'obj2': obj1})


    def testIllegalInterfaceError(self):

        registry = SimpleRegistry(I1)
        obj2 = Object2()

        self.failUnlessRaises(ZopeIllegalInterfaceError,
                              registry.register, 'obj2', obj2)
        

    def testDuplicateEntry(self):

        registry = SimpleRegistry(I1)
        obj1 = Object1()
        registry.register('obj1', obj1)

        self.failUnlessRaises(ZopeDuplicateRegistryEntryError,
                              registry.register, 'obj1', obj1)
        

    def testGet(self):

        registry = SimpleRegistry(I1)
        obj1 = Object1()
        obj2 = Object1()
        registry.objects = {'obj1': obj1, 'obj2': obj2}

        self.assertEqual(registry.get('obj1'), obj1)
        self.assertEqual(registry.get('obj2'), obj2)

        # Requesting an object that does not exist
        self.assertEqual(registry.get('obj3'), None)
        


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase( Test )


if __name__=='__main__':
    unittest.TextTestRunner().run( test_suite() )

