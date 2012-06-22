##############################################################################
#
# Copyright (c) 2012 Zope Foundation and Contributors.
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
"""Test adapter declaration helpers
"""
import unittest

class Test_adapter(unittest.TestCase):

    def _getTargetClass(self):
        from zope.component._declaration import adapter
        return adapter

    def _makeOne(self, *interfaces):
        return self._getTargetClass()(*interfaces)

    def test_ctor_no_interfaces(self):
        deco = self._makeOne()
        self.assertEqual(list(deco.interfaces), [])

    def test_ctor_w_interfaces(self):
        from zope.interface import Interface
        class IFoo(Interface):
            pass
        class IBar(Interface):
            pass
        deco = self._makeOne(IFoo, IBar)
        self.assertEqual(list(deco.interfaces), [IFoo, IBar])

    def test__call___w_class(self):
        from zope.interface import Interface
        class IFoo(Interface):
            pass
        class IBar(Interface):
            pass
        @self._makeOne(IFoo, IBar)
        class Baz(object):
            pass
        self.assertEqual(Baz.__component_adapts__, (IFoo, IBar))
        baz = Baz()
        self.assertRaises(AttributeError,
                          getattr, baz, '__component_adapts_')

    def test__call___w_non_class(self):
        from zope.interface import Interface
        class IFoo(Interface):
            pass
        class IBar(Interface):
            pass
        class Baz(object):
            pass
        deco = self._makeOne(IFoo, IBar)
        baz = deco(Baz())
        self.assertEqual(baz.__component_adapts__, (IFoo, IBar))
 

class Test_adapts(unittest.TestCase):

    def test_instances_not_affected(self):
        from zope.component._declaration import adapts
        class C(object):
            adapts()

        self.assertEqual(C.__component_adapts__, ())
        def _try():
            return C().__component_adapts__
        self.assertRaises(AttributeError, _try)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test_adapter),
        unittest.makeSuite(Test_adapts),
    ))
