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
$Id: test_wrapper.py,v 1.12 2003/05/12 15:44:41 mgedmin Exp $
"""
import pickle
import unittest

from zope.proxy.context import wrapper, getcontext, getobject, ContextWrapper
from zope.proxy.context import ContextMethod, ContextProperty, ContextAware
from zope.proxy.tests.test_proxy import Thing, ProxyTestCase

_marker = object()

class WrapperTestCase(ProxyTestCase):

    proxy_class = wrapper.Wrapper

    def new_proxy(self, o, c=None):
        return self.proxy_class(o, c)

    def test_constructor(self):
        o1 = object()
        o2 = object()
        o3 = object()
        w = self.new_proxy((o1, o2), o3)
        self.assertEquals(wrapper.getobject(w), (o1, o2))
        self.assert_(wrapper.getcontext(w) is o3)

    def test_subclass_constructor(self):
        class MyWrapper(self.proxy_class):
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
        class MyWrapper(self.proxy_class):
            def __init__(self, ob):
                super(MyWrapper, self).__init__(ob)
                self.foo = 1

        o = Thing()
        o.foo = 'not 1'
        o.bar = 2
        w = MyWrapper(o)
        self.assert_(w.foo == 1)
        self.assert_(w.bar == 2)

    def make_proxies(self, slot, fixed_retval=_marker):
        context = object()

        def doit(self, *args):
            self.retval = getcontext(self), args
            if fixed_retval is _marker:
                return self.retval
            else:
                return fixed_retval

        class ContextUnawareObj(object):
            pass
        setattr(ContextUnawareObj, slot, doit)
        proxy1 = self.new_proxy(ContextUnawareObj(), context)

        class ContextAwareObj(ContextAware):
            pass
        setattr(ContextAwareObj, slot, doit)
        proxy2 = self.new_proxy(ContextAwareObj(), context)

        class ContextMethodObj(object):
            pass
        setattr(ContextMethodObj, slot, ContextMethod(doit))
        proxy3 = self.new_proxy(ContextMethodObj(), context)

        return proxy1, proxy2, proxy3, context

    def test_normal_getattr(self):
        class X(object):
            def __init__(self, retval):
                self.args = None
                self.retval = retval
            def __getattr__(self, name):
                if name == '__del__':
                    # We don't want Python's gc to think that we have a
                    # __del__, otherwise cycles will not be collected.
                    raise AttributeError, name
                self.__dict__['args'] = self, name
                return self.__dict__['retval']
            def getArgs(self):
                return self.__dict__['args']

        context = object()

        x = X(23)
        p = self.new_proxy(x, context)
        self.assertEquals(p.foo, 23)
        # Nothing special happens; we don't rebind the self of __getattr__
        self.assertEquals(p.getArgs(), (x, 'foo'))
        self.assert_(p.getArgs()[0] is x)

    def test_ContextAware_getattr(self):
        class Y(ContextAware):
            def __init__(self, retval):
                self.args = None
                self.retval = retval
            def __getattr__(self, name):
                if name == '__del__':
                    # We don't want Python's gc to think that we have a
                    # __del__, otherwise cycles will not be collected.
                    raise AttributeError, name
                self.args = self, name
                return self.__dict__['retval']
            def getArgs(self):
                # Need to get __dict__ from the clean object, because it
                # is a special descriptor and complains bitterly about
                # being got from the wrong kind of object.
                return getobject(self).__dict__['args']

        y = Y(23)
        p = self.new_proxy(y, 23)
        self.assertEquals(p.foo, 23)
        # Nothing special happens; we don't rebind the self of __getattr__
        self.assertEquals(p.getArgs(), (y, 'foo'))
        self.assert_(p.getArgs()[0] is y)

    def test_ContextAware_doesnt_mess_up___class__(self):
        class C(ContextAware): pass
        self.assertEqual(ContextWrapper(C(), None).__class__, C)

    def test_ContextMethod_getattr(self):
        class Z(object):
            def __getattr__(self, name):
                return 23
            __getattr__ = ContextMethod(__getattr__)

        z = Z()
        self.assertRaises(TypeError, getattr, z, 'foo')
        p = self.new_proxy(z, 23)
        self.assertRaises(TypeError, getattr, p, 'foo')

        # This is the same behaviour that you get if you try to make
        # __getattr__ a classmethod.
        class ZZ(object):
            def __getattr__(self, name):
                return 23
            __getattr__ = classmethod(__getattr__)

        zz = ZZ()
        self.assertRaises(TypeError, getattr, zz, 'foo')

    def test_property(self):
        class X(object):
            def getFoo(self):
                self.called_with = self
                return 42
            def setFoo(self, value):
                self.called_with = self, value
            foo = property(getFoo, setFoo)
            context_foo = ContextProperty(getFoo, setFoo)
        x = X()
        p = self.new_proxy(x)
        self.assertEquals(p.foo, 42)
        self.assert_(x.called_with is x)
        self.assertEquals(p.context_foo, 42)
        self.assert_(x.called_with is p)
        p.foo = 24
        self.assertEquals(x.called_with, (x, 24))
        self.assert_(x.called_with[0] is x)
        p.context_foo = 24
        self.assertEquals(x.called_with, (p, 24))
        self.assert_(x.called_with[0] is p)

    def test_ContextAware_property(self):
        class Y(ContextAware):
            def getFoo(self):
                self.called_with = self
                return 42
            def setFoo(self, value):
                self.called_with = self, value
            foo = property(getFoo, setFoo)
        y = Y()
        p = self.new_proxy(y)
        self.assertEquals(p.foo, 42)
        self.assert_(y.called_with is p)
        p.foo = 24
        self.assertEquals(y.called_with, (p, 24))
        self.assert_(y.called_with[0] is p)

    def test_setattr(self):
        class X(object):
            def __setattr__(self, name, value):
                self.__dict__['value_called'] = self, name, value

        x = X()
        p = self.new_proxy(x)
        p.foo = 'bar'
        self.assertEqual(x.value_called, (p, 'foo', 'bar'))
        self.assert_(x.value_called[0] is x)

        class ContextAwareX(X, ContextAware):
            pass
        cax = ContextAwareX()
        p = self.new_proxy(cax)
        p.foo = 'bar'
        self.assertEqual(cax.value_called, (p, 'foo', 'bar'))
        self.assert_(cax.value_called[0] is cax)

        X.__setattr__ = ContextMethod(X.__setattr__)
        x = X()
        p = self.new_proxy(x)
        p.foo = 'bar'
        self.assertEqual(x.value_called, (p, 'foo', 'bar'))
        self.assert_(x.value_called[0] is x)

    def test_UnicodeAttrNames(self):
        class SomeObject(object):
            foo = 42
        obj = SomeObject()
        p = self.new_proxy(obj)
        self.assertEquals(getattr(p, u'foo'), 42)
        self.assertRaises(AttributeError, getattr, p, u'bar')
        self.assertRaises(UnicodeError, getattr, p, u'baz\u1234')
        setattr(p, u'bar', 23)
        self.assertEquals(p.bar, 23)
        self.assertRaises(UnicodeError, setattr, p, u'baz\u1234', 23)

    def test_getitem(self):
        p1, p2, p3, context = self.make_proxies('__getitem__')
        self.assertEquals(p1[42], (None, (42, )))
        self.assertEquals(p2[42], (context, (42, )))
        self.assertEquals(p3[42], (context, (42, )))
        # builtin
        p4 = self.new_proxy((1, 2), context)
        self.assertEquals(p4[0], 1)
        self.assertEquals(p4[1], 2)
        self.assertRaises(IndexError, p4.__getitem__, 2)

    def test_setitem(self):
        p1, p2, p3, context = self.make_proxies('__setitem__')
        p1[24] = 42
        p2[24] = 42
        p3[24] = 42
        self.assertEquals(p1.retval, (None, (24, 42)))
        self.assertEquals(p2.retval, (context, (24, 42)))
        self.assertEquals(p3.retval, (context, (24, 42)))
        # builtin
        p4 = self.new_proxy([1, 2], context)
        p4[1] = 3
        self.assertEquals(p4[1], 3)
        self.assertRaises(IndexError, p4.__setitem__, 2, 4)

    def test_delitem(self):
        p1, p2, p3, context = self.make_proxies('__delitem__')
        del p1[42]
        del p2[42]
        del p3[42]
        self.assertEquals(p1.retval, (None, (42, )))
        self.assertEquals(p2.retval, (context, (42, )))
        self.assertEquals(p3.retval, (context, (42, )))
        # builtin
        p4 = self.new_proxy([1, 2], context)
        del p4[1]
        self.assertEquals(p4, [1])
        self.assertRaises(IndexError, p4.__delitem__, 2)

    def test_iter(self):
        p1, p2, p3, context = self.make_proxies('__iter__', iter(()))
        iter(p1)
        iter(p2)
        iter(p3)
        self.assertEquals(p1.retval, (None, ()))
        self.assertEquals(p2.retval, (context, ()))
        self.assertEquals(p3.retval, (context, ()))

    def test_call(self):
        p1, p2, p3, context = self.make_proxies('__call__')
        self.assertEquals(p1('foo', 'bar'), (None, ('foo', 'bar')))
        self.assertEquals(p2('foo', 'bar'), (context, ('foo', 'bar')))
        self.assertEquals(p3('foo', 'bar'), (context, ('foo', 'bar')))

    def test_str(self):
        p1, p2, p3, context = self.make_proxies('__str__', 'foo')
        self.assertEquals(str(p1), 'foo')
        self.assertEquals(str(p2), 'foo')
        self.assertEquals(str(p3), 'foo')
        self.assertEquals(p1.retval, (None, ()))
        self.assertEquals(p2.retval, (context, ()))
        self.assertEquals(p3.retval, (context, ()))

    def test_contains(self):
        p1, p2, p3, context = self.make_proxies('__contains__', 1)
        self.assert_(42 in p1)
        self.assert_(42 in p2)
        self.assert_(42 in p3)
        self.assertEquals(p1.retval, (None, (42, )))
        self.assertEquals(p2.retval, (context, (42, )))
        self.assertEquals(p3.retval, (context, (42, )))

    def test_len(self):
        p1, p2, p3, context = self.make_proxies('__len__', 5)
        self.assertEquals(len(p1), 5)
        self.assertEquals(len(p2), 5)
        self.assertEquals(len(p3), 5)
        self.assertEquals(p1.retval, (None, ()))
        self.assertEquals(p2.retval, (context, ()))
        self.assertEquals(p3.retval, (context, ()))

        p1, p2, p3, context = self.make_proxies('__len__', 5)
        self.assertEquals(bool(p1), True)
        self.assertEquals(bool(p2), True)
        self.assertEquals(bool(p3), True)
        self.assertEquals(p1.retval, (None, ()))
        self.assertEquals(p2.retval, (context, ()))
        self.assertEquals(p3.retval, (context, ()))

        p1, p2, p3, context = self.make_proxies('__len__', 0)
        self.assertEquals(bool(p1), False)
        self.assertEquals(bool(p2), False)
        self.assertEquals(bool(p3), False)
        self.assertEquals(p1.retval, (None, ()))
        self.assertEquals(p2.retval, (context, ()))
        self.assertEquals(p3.retval, (context, ()))

    def test_nonzero(self):
        p1, p2, p3, context = self.make_proxies('__nonzero__', True)
        self.assertEquals(bool(p1), True)
        self.assertEquals(bool(p2), True)
        self.assertEquals(bool(p3), True)
        self.assertEquals(p1.retval, (None, ()))
        self.assertEquals(p2.retval, (context, ()))
        self.assertEquals(p3.retval, (context, ()))

        p1, p2, p3, context = self.make_proxies('__nonzero__', False)
        self.assertEquals(bool(p1), False)
        self.assertEquals(bool(p2), False)
        self.assertEquals(bool(p3), False)
        self.assertEquals(p1.retval, (None, ()))
        self.assertEquals(p2.retval, (context, ()))
        self.assertEquals(p3.retval, (context, ()))

    def test_nonzero_with_len(self):
        class ThingWithLenAndNonzero(object):
            len_called = False
            nonzero_called = False
            retval = None

            def __len__(self):
                self.len_called = True
                self.retval = self
                return 0

            def __nonzero__(self):
                self.nonzero_called = True
                self.retval = self
                return False

        obj = ThingWithLenAndNonzero()
        w = self.new_proxy(obj)
        self.assertEquals(bool(w), False)
        self.assertEquals(obj.nonzero_called, True)
        self.assertEquals(obj.len_called, False)
        self.assert_(obj.retval is obj)

        ThingWithLenAndNonzero.__nonzero__ = ContextMethod(
            ThingWithLenAndNonzero.__nonzero__.im_func)

        obj = ThingWithLenAndNonzero()
        w = self.new_proxy(obj)
        self.assertEquals(bool(w), False)
        self.assertEquals(obj.nonzero_called, True)
        self.assertEquals(obj.len_called, False)
        self.assert_(obj.retval is w)

    # Tests for wrapper module globals

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

        w = self.proxy_class(None, name="myobject")
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
