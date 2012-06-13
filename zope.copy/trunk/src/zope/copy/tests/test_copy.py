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
import unittest

class Test_copy(unittest.TestCase):

    def setUp(self):
        from zope.component.globalregistry import base
        base.__init__('base') # blow away previous registrations
    tearDown = setUp

    def _callFUT(self, obj):
        from zope.copy import copy
        return copy(obj)

    def test_wo_hooks(self):
        from zope.copy.examples import Demo
        demo = Demo()
        demo.freeze()
        self.assertTrue(demo.isFrozen())
        copied = self._callFUT(demo)
        self.assertFalse(copied is demo)
        self.assertTrue(isinstance(copied, Demo))
        self.assertTrue(copied.isFrozen())

    def test_w_simple_hook(self):
        from zope.component import provideAdapter
        from zope.interface import implementer
        from zope.copy.interfaces import ICopyHook
        from zope.copy.examples import Data
        from zope.copy.examples import Demo
        demo = Demo()
        demo.freeze()
        def _factory(obj, register):
            return None
        @implementer(ICopyHook)
        def data_copyfactory(obj):
            return _factory
        provideAdapter(data_copyfactory, (Data,))
        copied = self._callFUT(demo)
        self.assertFalse(copied is demo)
        self.assertTrue(isinstance(copied, Demo))
        self.assertFalse(copied.isFrozen())

    def test_subobject_wo_post_copy_hook(self):
        from zope.location.location import Location
        from zope.location.location import locate
        from zope.copy.examples import Subobject
        o = Location()
        s = Subobject()
        o.subobject = s
        locate(s, o, 'subobject')
        self.assertTrue(s.__parent__ is o)
        self.assertEqual(o.subobject(), 0)
        self.assertEqual(o.subobject(), 1)
        self.assertEqual(o.subobject(), 2)
        c = self._callFUT(o)
        self.assertTrue(c.subobject.__parent__ is c)
        self.assertEqual(c.subobject(), 3)
        self.assertEqual(o.subobject(), 3)

    def test_subobject_w_post_copy_hook(self):
        from zope.component import provideAdapter
        from zope.interface import implementer
        from zope.copy.interfaces import ICopyHook
        from zope.location.location import Location
        from zope.location.location import locate
        from zope.copy.examples import Subobject
        o = Location()
        s = Subobject()
        o.subobject = s
        locate(s, o, 'subobject')
        self.assertTrue(s.__parent__ is o)
        self.assertEqual(o.subobject(), 0)
        self.assertEqual(o.subobject(), 1)
        self.assertEqual(o.subobject(), 2)
        @implementer(ICopyHook)
        def subobject_copyfactory(original):
            def factory(obj, register):
                obj = Subobject()
                def reparent(translate):
                    obj.__parent__ = translate(original.__parent__)
                register(reparent)
                return obj
            return factory
        provideAdapter(subobject_copyfactory, (Subobject,))
        c = self._callFUT(o)
        self.assertTrue(c.subobject.__parent__ is c)
        self.assertEqual(c.subobject(), 0)
        self.assertEqual(o.subobject(), 3)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test_copy),
    ))
