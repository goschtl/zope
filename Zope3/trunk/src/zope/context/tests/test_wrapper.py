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
import pickle
import unittest

from zope.proxy.context import wrapper
from zope.proxy.tests.test_proxy import Comparable, Thing, ProxyTestCase


class WrapperTestCase(ProxyTestCase):
    def new_proxy(self, o, c=None):
        return wrapper.Wrapper(o, c)

    def test_constructor(self):
        o1 = object()
        o2 = object()
        o3 = object()
        w = self.new_proxy((o1, o2), o3)
        self.assertEquals(wrapper.getobject(w), (o1, o2))
        self.assert_(wrapper.getcontext(w) is o3)


    def test_subclass_constructor(self):
        class MyWrapper(wrapper.Wrapper):
            def __init__(self, *args, **kwds):
                super(MyWrapper, self).__init__('foo', **kwds)

        w = MyWrapper(1, 2, key='value')
        self.assertEquals(wrapper.getobject(w), 'foo')
        self.assertEquals(wrapper.getdict(w), {'key': 'value'})

        # __new__ catches too many positional args:
        self.assertRaises(TypeError, MyWrapper, 1, 2, 3)

    def test_wrapper_basics(self):
        o1 = 1
        o2 = 12
        w = self.new_proxy(o1)
        self.assert_(o1 is wrapper.getobject(w))
        self.assert_(wrapper.getdict(w) is None)
        d = wrapper.getdictcreate(w)
        self.assert_(wrapper.getdictcreate(w) is d)

        c = 'context'
        wrapper.setcontext(w, c)
        self.assert_(wrapper.getcontext(w) is c)
        wrapper.setcontext(w, None)
        self.assert_(wrapper.getcontext(w) is None)

        wrapper.setobject(w, o2)
        self.assert_(wrapper.getobject(w) is o2)

        # test 2-argument version of constructor
        o = object()
        w = self.new_proxy(o, c)
        self.assert_(wrapper.getobject(w) is o)
        self.assert_(wrapper.getcontext(w) is c)

    def test_wrapper_subclass_attributes(self):
        class MyWrapper(wrapper.Wrapper):
            def __init__(self, ob):
                super(MyWrapper, self).__init__(ob)
                self.foo = 1

        o = Thing()
        o.foo = 'not 1'
        o.bar = 2
        w = MyWrapper(o)
        self.assert_(w.foo == 1)
        self.assert_(w.bar == 2)

    def test_getobject(self):
        obj1 = object()
        obj2 = object()
        w = self.new_proxy(obj1)
        self.assert_(wrapper.getobject(w) is obj1)
        wrapper.setobject(w, obj2)
        self.assert_(wrapper.getobject(w) is obj2)
        self.assert_(wrapper.getobject(None) is None)
        self.assert_(wrapper.getobject(obj1) is obj1)

    def test_getbaseobject(self):
        obj = object()
        self.assert_(wrapper.getbaseobject(obj) is obj)
        w1 = self.new_proxy(obj)
        self.assert_(wrapper.getbaseobject(w1) is obj)
        w = self.new_proxy(w1)
        w = self.new_proxy(w)
        w = self.new_proxy(w)
        w = self.new_proxy(w)
        w = self.new_proxy(w)
        self.assert_(wrapper.getbaseobject(w) is obj)
        wrapper.setobject(w1, None)
        self.assert_(wrapper.getbaseobject(w) is None)
        obj = object()
        wrapper.setobject(w1, obj)
        self.assert_(wrapper.getbaseobject(w) is obj)

    def test_getcontext(self):
        context = object()
        w = self.new_proxy(None, context)
        self.assert_(wrapper.getcontext(w) is context)
        self.assert_(wrapper.getcontext(self.new_proxy(None)) is None)
        self.assert_(wrapper.getcontext(object()) is None)

    def check_getinnercontext(self, context):
        obj = object()
        self.assert_(wrapper.getinnercontext(obj) is None)
        w1 = self.new_proxy(obj, context)
        self.assert_(wrapper.getinnercontext(w1) is context)
        w = self.new_proxy(w1, object())
        w = self.new_proxy(w)
        w = self.new_proxy(w, object())
        w = self.new_proxy(w)
        w = self.new_proxy(w, object())
        self.assert_(wrapper.getinnercontext(w) is context)
        wrapper.setcontext(w1, None)
        self.assert_(wrapper.getinnercontext(w) is None)
        context = object()
        wrapper.setcontext(w1, context)
        self.assert_(wrapper.getinnercontext(w) is context)

    def test_getinnercontext(self):
        self.check_getinnercontext(None)
        self.check_getinnercontext(object())

    def test_getinnerwrapper(self):
        context = object()
        o = object()
        w1 = self.new_proxy(o)
        w2 = self.new_proxy(w1, context)
        x = wrapper.getinnerwrapper(w2)
        self.assert_(x is w1)
        self.assert_(wrapper.getinnerwrapper(o) is o)

    def test_getdict(self):
        w = self.new_proxy(None)
        self.assert_(wrapper.getdict(w) is None)
        d = wrapper.getdictcreate(w)
        self.assert_(wrapper.getdict(w) is d)
        self.assert_(wrapper.getdictcreate(w) is d)
        self.assert_(wrapper.getdict(w) is d)

        w = wrapper.Wrapper(None, name="myobject")
        d = wrapper.getdict(w)
        self.assert_(d is not None)
        self.assert_(wrapper.getdictcreate(w) is d)
        self.assert_(wrapper.getdictcreate(w) is d)
        self.assert_(len(d) == 1)

    def test_setobject(self):
        obj1 = object()
        obj2 = object()
        w = self.new_proxy(obj1)
        self.assert_(wrapper.getobject(w) is obj1)
        wrapper.setobject(w, obj2)
        self.assert_(wrapper.getobject(w) is obj2)

    def test_setcontext(self):
        w = self.new_proxy(None)
        context = object()
        wrapper.setcontext(w, context)
        self.assert_(wrapper.getcontext(w) is context)

    def test_pickle_prevention(self):
        w = self.new_proxy(Thing())
        self.assertRaises(pickle.PicklingError,
                          pickle.dumps, w)


def test_suite():
    return unittest.makeSuite(WrapperTestCase)


if __name__ == "__main__":
    import sys
    runner = unittest.TextTestRunner(sys.stdout)
    result = runner.run(test_suite())
    newerrs = len(result.errors) + len(result.failures)
    sys.exit(newerrs and 1 or 0)
