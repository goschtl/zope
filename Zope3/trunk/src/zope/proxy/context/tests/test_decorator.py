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
$Id: test_decorator.py,v 1.8 2003/05/12 15:44:41 mgedmin Exp $
"""
import unittest

from zope.proxy.context import wrapper, decorator
from zope.proxy.context.tests.test_wrapper import WrapperTestCase

class DecoratorTestCase(WrapperTestCase):

    proxy_class = decorator.Decorator

    def new_proxy(self, o, c=None, mixinfactory=None, names=None,
                  attrdict=None, inner=None):
        return self.proxy_class(o, c, mixinfactory, names, attrdict, inner)

    def test_subclass_constructor(self):
        class MyWrapper(self.proxy_class):
            def __init__(self, *args, **kwds):
                super(MyWrapper, self).__init__('foo', **kwds)

        w = MyWrapper(1, 2, key='value')
        self.assertEquals(wrapper.getobject(w), 'foo')
        self.assertEquals(wrapper.getdict(w), {'key': 'value'})

        # __new__ catches too many positional args:
        self.assertRaises(TypeError, MyWrapper, 1, 2, 3, 4, 5, 6, 7)

    def test_decorator_basics(self):
        # check that default arguments are set correctly as per the interface
        obj = object()
        w = self.proxy_class(obj)
        self.assert_(wrapper.getcontext(w) is None)
        self.assert_(decorator.getmixin(w) is None)
        self.assertEquals(decorator.getnames(w), ())
        self.assert_(decorator.getmixinfactory(w) is None)
        self.assert_(decorator.getinner(w) is obj)

        # getnamesdict is not in the official decorator interface, but it
        # is provided so that the caching dict can be unit-tested from Python.

        # dictproxy instances are not comparable for equality with dict
        # instances
        # self.assertEquals(decorator.getnamesdict(w), {})
        self.assertEquals(len(decorator.getnamesdict(w)), 0)

        # check that non-default arguments are set correctly
        class SomeObject(object):
            def bar(self):
                pass
        obj = SomeObject()

        class MixinFactory(object):
            def __init__(self, inner, outer):
                self.inner = inner
                self.outer = outer
            def foo(self):
                pass
            def bar(self):
                pass

        c = object()
        f = MixinFactory
        n = ('foo',)
        ad = {'baz':23}
        inner = object()
        w = self.proxy_class(obj, c, f, n, ad, inner)

        keys = decorator.getnamesdict(w).keys()
        keys.sort()
        self.assertEquals(keys, ['baz', 'foo'])
        self.assertEquals(decorator.getnamesdict(w)['baz'], 23)

        self.assert_(wrapper.getcontext(w) is c)
        self.assert_(decorator.getmixin(w) is None)
        self.assertEquals(decorator.getnames(w), n)
        self.assert_(decorator.getmixinfactory(w) is f)
        self.assert_(decorator.getinner(w) is inner)

        # Check that accessing a non-name does not create the mixin.
        w.bar()
        self.assert_(decorator.getmixin(w) is None)
        # Check that accessing something from the attrdict does not create the
        # mixin.
        w.baz
        self.assert_(decorator.getmixin(w) is None)

        # Check that accessing a name creates the mixin.
        w.foo()
        mixin = decorator.getmixin(w)
        self.assert_(type(mixin) is MixinFactory)

        # Check that the mixin factory is constructed with the correct args.
        self.assert_(mixin.inner is inner)
        self.assert_(mixin.outer is w)

        # check that getmixincreate works, and incidentally that getinner
        # returns the same as getobject when there is no inner specified

        # note, neither 'attrdict' nor 'inner' given
        w = self.proxy_class(obj, c, f, n, None, None)
        self.assert_(decorator.getmixin(w) is None)
        mixin = decorator.getmixincreate(w)
        self.assert_(type(mixin) is MixinFactory)
        self.assert_(decorator.getmixin(w) is mixin)
        self.assert_(mixin.inner is obj)

    def test_mixin_created_once_only(self):
        class SomeObject(object):
            def bar(self):
                pass
        obj = SomeObject()

        class MixinFactory(object):
            def foo(self):
                pass
            def bar(self):
                pass

        c = object()
        f = MixinFactory
        n = ('foo', 'spoo', 'someinstanceattr')
        w = self.proxy_class(obj, c, f, n)

        self.assert_(decorator.getmixin(w) is None)
        self.assert_(decorator.getmixinfactory(w) is f)

        w.foo()
        mixin = decorator.getmixin(w)
        self.assert_(type(mixin) is MixinFactory)
        w.foo()
        mixin2 = decorator.getmixin(w)
        self.assert_(mixin is mixin2)

    def test_getattrAspectsThatAreNotTestedElsewhere(self):
        class SomeObject(object):
            def bar(self):
                pass
        obj = SomeObject()

        class MixinFactory(object):
            def __init__(self, inner, outer):
                self.someinstanceattr = 42
            def foo(self):
                pass
            def bar(self):
                pass
            spoo = 23

        c = object()
        f = MixinFactory
        n = ('foo', 'spoo', 'someinstanceattr')
        w = self.proxy_class(obj, c, f, n)

        self.assertEqual(w.spoo, 23)
        # Check that getting a unicode attr is handled correctly.
        self.assertEqual(getattr(w, u'spoo'), 23)

        # Check that an attribute on the mixin object can be retrieved.
        self.assertEquals(w.someinstanceattr, 42)
        self.assertEquals(getattr(w, u'someinstanceattr'), 42)

    def test_horribleUnicodeAbuse(self):
        class SomeObject(object):
            def bar(self):
                pass
        obj = SomeObject()

        class MixinFactory(object):
            def __init__(self, inner, outer):
                self.someinstanceattr = 42
            def foo(self):
                pass
            def bar(self):
                pass
            spoo = 23

        c = object()
        f = MixinFactory
        n = ('foo', 'spoo', u's\u2323g', 'someinstanceattr')
        self.assertRaises(TypeError, self.proxy_class, obj, c, f, n)

    def test_typeerror_if_no_factory(self):
        w = self.proxy_class(object(), None, None, ('foo',))
        self.assertRaises(TypeError, getattr, w, 'foo')
        self.assertRaises(TypeError, decorator.getmixincreate)

    def test_decorator_setattr(self):
        # setattr includes delattr, seeing as we're testing something written
        # in C, and delattr is a special case of setattr at the C level.
        obj = object()

        class MixinFactory(object):
            def __init__(self, inner, outer):
                pass
            def setFoo(self, value):
                self.fooval = value
            def getFoo(self):
                return self.fooval
            def delFoo(self):
                del self.fooval
            foo = property(getFoo, setFoo, delFoo)

        w = self.proxy_class(obj, None, MixinFactory, ('foo',), {'baz': 23})
        mixin = decorator.getmixincreate(w)
        self.failIf(hasattr(mixin, 'fooval'))
        self.assertRaises(AttributeError, getattr, w, 'foo')
        self.assertRaises(AttributeError, delattr, w, 'foo')
        w.foo = 'skidoo'
        self.assertEquals(mixin.fooval, 'skidoo')
        del w.foo
        self.failIf(hasattr(mixin, 'fooval'))

        # test setattr unicode attr string
        setattr(w, u'foo', 'skidoo')
        self.assertEquals(mixin.fooval, 'skidoo')
        delattr(w, u'foo')
        self.failIf(hasattr(mixin, 'fooval'))

        # Check that trying to set something in attrdict fails.
        self.assertRaises(AttributeError, setattr, w, 'baz', 23)
        self.assertRaises(AttributeError, delattr, w, 'baz')

    def test_decorated_slots(self):
        obj = object()

        names = ('__len__', '__getitem__', '__setitem__', '__str__',
                 '__contains__', '__call__', '__nonzero__', '__iter__',
                 'next')

        dummy_iter = iter(range(5))

        class MixinFactory(object):
            def __init__(self, inner, outer):
                pass
            count = 0
            def __len__(self):
                self.called = 'len'
                return 5
            def __nonzero__(self):
                self.called = 'nonzero'
                return False
            def __getitem__(self, key):
                self.called = 'getitem'
                return 5
            def __setitem__(self, key, value):
                self.called = 'setitem'
            def __str__(self):
                self.called = 'str'
                return '5'
            def __contains__(self, key):
                self.called = 'contains'
                return True
            def __call__(self):
                self.called = 'call'
                return 'skidoo'
            def __iter__(self):
                self.called = 'iter'
                return self
            def next(self):
                self.called = 'next'
                self.count += 1
                if self.count == 5:
                    self.count = 0
                    raise StopIteration
                return self.count

        w = self.proxy_class(obj, None, MixinFactory, names)

        mixin = decorator.getmixincreate(w)
        self.assertRaises(AttributeError, getattr, mixin, 'called')

        self.assertEquals(len(w), 5)
        self.assertEquals(mixin.called, 'len')
        del mixin.called

        self.assertEquals(w[3], 5)
        self.assertEquals(mixin.called, 'getitem')
        del mixin.called

        w[3] = 5
        self.assertEquals(mixin.called, 'setitem')
        del mixin.called

        self.assertEquals(str(w), '5')
        self.assertEquals(mixin.called, 'str')
        del mixin.called

        self.assert_(5 in w)
        self.assertEquals(mixin.called, 'contains')
        del mixin.called

        self.assertEquals(w(), 'skidoo')
        self.assertEquals(mixin.called, 'call')
        del mixin.called

        self.assertEquals(bool(w), False)
        self.assertEquals(mixin.called, 'nonzero')
        del mixin.called

        # Test case where mixin doesn't provide a __nonzero__ but does
        # provide a __len__.
        del MixinFactory.__nonzero__
        self.assertEquals(bool(w), True)
        self.assertEquals(mixin.called, 'len')
        del mixin.called

        self.assertEquals(iter(w), mixin)
        self.assertEquals(mixin.called, 'iter')
        del mixin.called

        self.assertEquals(w.next(), 1)
        self.assertEquals(mixin.called, 'next')
        self.assertEquals([i for i in iter(w)], [2, 3, 4])
        del mixin.called

    def test_decorated_iterable(self):
        obj = object()
        a = [1, 2, 3]
        b = []
        factory = lambda inner, outer: a
        names = ('__iter__',)
        for x in self.proxy_class(obj, None, factory, names):
            b.append(x)
        self.assertEquals(a, b)

    def test_iteration_over_decorator(self):
        # Wrap an iterator before starting iteration.
        # PyObject_GetIter() will still be called on the proxy.
        obj = object()
        a = [1, 2, 3]
        b = []
        factory = lambda inner, outer: iter(a)
        names = ('__iter__',)
        for x in self.proxy_class(obj, None, factory, names):
            b.append(x)
        self.assertEquals(a, b)
        t = tuple(self.proxy_class(obj, None, factory, names))
        self.assertEquals(t, (1, 2, 3))

    def XXXtest_iteration_using_decorator(self):
        # XXX This test is taken from test_iteration_using_proxy in
        # test_proxy.py. It doesn't work when adapted for decoration.
        # This needs looking at, but it is something of an edge case, and
        # so isn't a priority.

        # Wrap an iterator within the iteration protocol, expecting it
        # still to work.  PyObject_GetIter() will not be called on the
        # proxy, so the tp_iter slot won't unwrap it.

        class Iterable:
            def __init__(self, test, data):
                self.test = test
                self.data = data
            def __iter__(self):
                obj = object()
                names = ('__iter__', 'next')
                factory = lambda inner, outer: iter(self.data)
                return self.test.proxy_class(obj, None, factory, names)

        a = [1, 2, 3]
        b = []
        for x in Iterable(self, a):
            b.append(x)
        self.assertEquals(a, b)

def test_suite():
    return unittest.makeSuite(DecoratorTestCase)


if __name__ == "__main__":
    import sys
    runner = unittest.TextTestRunner(sys.stdout)
    result = runner.run(test_suite())
    newerrs = len(result.errors) + len(result.failures)
    sys.exit(newerrs and 1 or 0)
