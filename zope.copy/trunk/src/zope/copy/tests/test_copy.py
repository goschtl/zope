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


class Test_clone(unittest.TestCase):

    def setUp(self):
        from zope.component.globalregistry import base
        base.__init__('base') # blow away previous registrations
    tearDown = setUp

    def _callFUT(self, obj):
        from zope.copy import clone
        return clone(obj)

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


class Test_copy(unittest.TestCase):

    def setUp(self):
        from zope.component.globalregistry import base
        base.__init__('base') # blow away previous registrations
    tearDown = setUp

    def _callFUT(self, obj):
        from zope.copy import copy
        return copy(obj)

    def test_clears_attrs(self):
        from zope.copy.examples import Demo
        parent = Demo()
        demo = Demo()
        demo.__parent__ = parent
        demo.__name__ = 'demo'
        copied = self._callFUT(demo)
        self.assertFalse(copied is demo)
        self.assertTrue(isinstance(copied, Demo))
        self.assertEqual(copied.__parent__, None)
        self.assertEqual(copied.__name__, None)

    def test_w_readonly___parent___and___name__(self):
        global Foo #make unpicklable
        parent = object()
        class Foo(object):
            @property
            def __parent__(self):
                return parent
            @property
            def __name__(self):
                return 'foo'
        foo = Foo()
        copied = self._callFUT(foo)
        self.assertFalse(copied is foo)
        self.assertTrue(isinstance(copied, Foo))
        self.assertTrue(copied.__parent__ is parent)
        self.assertEqual(copied.__name__, 'foo')


class CopyPersistentTests(unittest.TestCase):

    def setUp(self):
        from zope.component.globalregistry import base
        base.__init__('base') # blow away previous registrations
    tearDown = setUp

    def _getTargetClass(self):
        from zope.copy import CopyPersistent
        return CopyPersistent

    def _makeOne(self, obj):
        return self._getTargetClass()(obj)

    def test_ctor(self):
        obj = object()
        cp = self._makeOne(obj)
        self.assertTrue(cp.toplevel is obj)
        self.assertEqual(cp.pids_by_id, {})
        self.assertEqual(cp.others_by_pid, {})
        self.assertEqual(cp.registered, [])

    def test_id_wo_hook(self):
        obj = object()
        cp = self._makeOne(obj)
        self.assertEqual(cp.id(obj), None)

    def test_id_w_hook_already_cached(self):
        from zope.component import provideAdapter
        from zope.interface import implementer
        from zope.interface import Interface
        from zope.copy.interfaces import ICopyHook
        obj = object()
        cp = self._makeOne(obj)
        cp.pids_by_id[id(obj)] = 'PID'
        def _factory(obj, register):
            return None
        @implementer(ICopyHook)
        def copyfactory(obj):
            return _factory
        provideAdapter(copyfactory, (Interface,))
        self.assertEqual(cp.id(obj), 'PID')

    def test_id_w_hook_raising_ResumeCopy(self):
        from zope.component import provideAdapter
        from zope.interface import implementer
        from zope.interface import Interface
        from zope.copy.interfaces import ICopyHook
        from zope.copy.interfaces import ResumeCopy
        obj = object()
        cp = self._makeOne(obj)
        def _factory(obj, register):
            raise ResumeCopy()
        @implementer(ICopyHook)
        def copyfactory(obj):
            return _factory
        provideAdapter(copyfactory, (Interface,))
        self.assertEqual(cp.id(obj), None)

    def test_id_w_hook_normal(self):
        from zope.component import provideAdapter
        from zope.interface import implementer
        from zope.interface import Interface
        from zope.copy.interfaces import ICopyHook
        obj = object()
        cp = self._makeOne(obj)
        def _factory(obj, register):
            return None
        @implementer(ICopyHook)
        def copyfactory(obj):
            return _factory
        provideAdapter(copyfactory, (Interface,))
        self.assertEqual(cp.id(obj), 1)
        obj2 = object()
        self.assertEqual(cp.id(obj2), 2)
        self.assertEqual(cp.pids_by_id, {id(obj): 1, id(obj2): 2})
        self.assertEqual(cp.others_by_pid, {1: None, 2: None})


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test_clone),
        unittest.makeSuite(Test_copy),
        unittest.makeSuite(CopyPersistentTests),
    ))
