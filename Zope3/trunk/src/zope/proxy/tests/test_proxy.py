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
"""Test base proxy class.

$Id: test_proxy.py,v 1.12 2003/06/03 22:46:27 jim Exp $
"""
import pickle
import unittest
from zope.testing.doctestunit import DocTestSuite
from zope.proxy import ProxyBase

class Thing:
    pass

class Comparable:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if hasattr(other, "value"):
            other = other.value
        return self.value == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if hasattr(other, "value"):
            other = other.value
        return self.value < other

    def __ge__(self, other):
        return not self.__lt__(other)

    def __le__(self, other):
        if hasattr(other, "value"):
            other = other.value
        return self.value <= other

    def __gt__(self, other):
        return not self.__le__(other)

    def __repr__(self):
        return "<Comparable: %r>" % self.value


class ProxyTestCase(unittest.TestCase):

    proxy_class = ProxyBase

    def setUp(self):
        self.x = Thing()
        self.p = self.new_proxy(self.x)

    def new_proxy(self, o):
        return self.proxy_class(o)

    def test_constructor(self):
        o = object()
        self.assertRaises(TypeError, self.proxy_class, o, o)
        self.assertRaises(TypeError, self.proxy_class, o, key='value')
        self.assertRaises(TypeError, self.proxy_class, key='value')

    def test_subclass_constructor(self):
        # NB This leaks due to a bug in Python 2.2.2.
        #    The leak is fixed in the release22-maint branch in Python CVS
        #    (and this in Python 2.2.3), and in Python 2.3.
        class MyProxy(self.proxy_class):
            def __new__(cls, *args, **kwds):
                return super(MyProxy, cls).__new__(cls, *args, **kwds)
            def __init__(self, *args, **kwds):
                super(MyProxy, self).__init__(*args, **kwds)
        o1 = object()
        o2 = object()
        o = MyProxy((o1, o2))

        self.assertEquals(o1, o[0])
        self.assertEquals(o2, o[1])

        self.assertRaises(TypeError, MyProxy, o1, o2)
        self.assertRaises(TypeError, MyProxy, o1, key='value')
        self.assertRaises(TypeError, MyProxy, key='value')

        # Check that are passed to __init__() overrides what's passed
        # to __new__().
        class MyProxy2(self.proxy_class):
            def __new__(cls, *args, **kwds):
                return super(MyProxy2, cls).__new__(cls, 'value')

        p = MyProxy2('splat!')
        self.assertEquals(list(p), list('splat!'))

        class MyProxy3(MyProxy2):
            def __init__(self, arg):
                assert list(self) == list('value')
                super(MyProxy3, self).__init__('another')

        p = MyProxy3('notused')
        self.assertEquals(list(p), list('another'))

    def test_proxy_attributes(self):
        o = Thing()
        o.foo = 1
        w = self.new_proxy(o)
        self.assert_(w.foo == 1)

    def test___class__(self):
        o = object()
        w = self.new_proxy(o)
        self.assert_(w.__class__ is o.__class__)

    def test_pickle_prevention(self):
        w = self.new_proxy(Thing())
        self.assertRaises(pickle.PicklingError,
                          pickle.dumps, w)

    def test_proxy_equality(self):
        w = self.new_proxy('foo')
        self.assertEquals(w, 'foo')

        o1 = Comparable(1)
        o2 = Comparable(1.0)
        o3 = Comparable("splat!")

        w1 = self.new_proxy(o1)
        w2 = self.new_proxy(o2)
        w3 = self.new_proxy(o3)

        self.assertEquals(o1, w1)
        self.assertEquals(o1, w2)
        self.assertEquals(o2, w1)
        self.assertEquals(w1, o2)
        self.assertEquals(w2, o1)

        self.assertNotEquals(o3, w1)
        self.assertNotEquals(w1, o3)
        self.assertNotEquals(w3, o1)
        self.assertNotEquals(o1, w3)

    def test_proxy_ordering_lt(self):
        o1 = Comparable(1)
        o2 = Comparable(2.0)

        w1 = self.new_proxy(o1)
        w2 = self.new_proxy(o2)

        self.assert_(w1 < w2)
        self.assert_(w1 <= w2)
        self.assert_(o1 < w2)
        self.assert_(o1 <= w2)
        self.assert_(w1 < o2)
        self.assert_(w2 <= o2)

    def test_proxy_callable(self):
        w = self.new_proxy({}.get)
        self.assert_(callable(w))

    def test_proxy_item_protocol(self):
        w = self.new_proxy({})
        self.assertRaises(KeyError, lambda: w[1])
        w[1] = 'a'
        self.assertEquals(w[1], 'a')
        del w[1]
        self.assertRaises(KeyError, lambda: w[1])
        def del_w_1():
            del w[1]
        self.assertRaises(KeyError, del_w_1)

    def test_wrapped_iterable(self):
        a = [1, 2, 3]
        b = []
        for x in self.new_proxy(a):
            b.append(x)
        self.assertEquals(a, b)

    def test_iteration_over_proxy(self):
        # Wrap an iterator before starting iteration.
        # PyObject_GetIter() will still be called on the proxy.
        a = [1, 2, 3]
        b = []
        for x in self.new_proxy(iter(a)):
            b.append(x)
        self.assertEquals(a, b)
        t = tuple(self.new_proxy(iter(a)))
        self.assertEquals(t, (1, 2, 3))

    def test_iteration_using_proxy(self):
        # Wrap an iterator within the iteration protocol, expecting it
        # still to work.  PyObject_GetIter() will not be called on the
        # proxy, so the tp_iter slot won't unwrap it.

        class Iterable:
            def __init__(self, test, data):
                self.test = test
                self.data = data
            def __iter__(self):
                return self.test.new_proxy(iter(self.data))

        a = [1, 2, 3]
        b = []
        for x in Iterable(self, a):
            b.append(x)
        self.assertEquals(a, b)

    def test_bool_wrapped_None(self):
        w = self.new_proxy(None)
        self.assertEquals(not w, 1)

    # Numeric ops.

    unops = [
        "-x", "+x", "abs(x)", "~x",
        "int(x)", "long(x)", "float(x)",
        ]

    def test_unops(self):
        P = self.new_proxy
        for expr in self.unops:
            x = 1
            y = eval(expr)
            x = P(1)
            z = eval(expr)
            self.assertEqual(z, y,
                             "x=%r; expr=%r" % (x, expr))

    def test_odd_unops(self):
        # unops that don't return a proxy
        P = self.new_proxy
        for func in hex, oct, lambda x: not x:
            self.assertEqual(func(P(100)), func(100))

    binops = [
        "x+y", "x-y", "x*y", "x/y", "divmod(x, y)", "x**y", "x//y",
        "x<<y", "x>>y", "x&y", "x|y", "x^y",
        ]

    def test_binops(self):
        P = self.new_proxy
        for expr in self.binops:
            first = 1
            for x in [1, P(1)]:
                for y in [2, P(2)]:
                    if first:
                        z = eval(expr)
                        first = 0
                    else:
                        self.assertEqual(eval(expr), z,
                                         "x=%r; y=%r; expr=%r" % (x, y, expr))

    def test_inplace(self):
        # XXX should test all inplace operators...
        P = self.new_proxy

        pa = P(1)
        pa += 2
        self.assertEqual(pa, 3)

        a = [1, 2, 3]
        pa = qa = P(a)
        pa += [4, 5, 6]
        self.failUnless(pa is qa)
        self.assertEqual(a, [1, 2, 3, 4, 5, 6])

        pa = P(2)
        pa **= 2
        self.assertEqual(pa, 4)

    def test_coerce(self):
        P = self.new_proxy

        # Before 2.3, coerce() of two proxies returns them unchanged
        import sys
        fixed_coerce = sys.version_info >= (2, 3, 0)

        x = P(1)
        y = P(2)
        a, b = coerce(x, y)
        self.failUnless(a is x and b is y)

        x = P(1)
        y = P(2.1)
        a, b = coerce(x, y)
        self.failUnless(a == 1.0)
        self.failUnless(b is y)
        if fixed_coerce:
            self.failUnless(a.__class__ is float, a.__class__)

        x = P(1.1)
        y = P(2)
        a, b = coerce(x, y)
        self.failUnless(a is x)
        self.failUnless(b == 2.0)
        if fixed_coerce:
            self.failUnless(b.__class__ is float, b.__class__)

        x = P(1)
        y = 2
        a, b = coerce(x, y)
        self.failUnless(a is x)
        self.failUnless(b is y)

        x = P(1)
        y = 2.1
        a, b = coerce(x, y)
        self.failUnless(a.__class__ is float, a.__class__)
        self.failUnless(b is y)

        x = P(1.1)
        y = 2
        a, b = coerce(x, y)
        self.failUnless(a is x)
        self.failUnless(b.__class__ is float, b.__class__)

        x = 1
        y = P(2)
        a, b = coerce(x, y)
        self.failUnless(a is x)
        self.failUnless(b is y)

        x = 1.1
        y = P(2)
        a, b = coerce(x, y)
        self.failUnless(a is x)
        self.failUnless(b.__class__ is float, b.__class__)

        x = 1
        y = P(2.1)
        a, b = coerce(x, y)
        self.failUnless(a.__class__ is float, a.__class__)
        self.failUnless(b is y)


def test_isProxy():
    """
    >>> from zope.proxy import ProxyBase, isProxy
    >>> class P1(ProxyBase):
    ...     pass
    >>> class P2(ProxyBase):
    ...     pass
    >>> class C:
    ...     pass
    >>> c = C()
    >>> int(isProxy(c))
    0
    >>> p = P1(c)
    >>> int(isProxy(p))
    1
    >>> int(isProxy(p, P1))
    1
    >>> int(isProxy(p, P2))
    0
    >>> p = P2(p)
    >>> int(isProxy(p, P1))
    1
    >>> int(isProxy(p, P2))
    1

    """

def test_getProxiedObject():
    """
    >>> from zope.proxy import ProxyBase, getProxiedObject
    >>> class C:
    ...     pass
    >>> c = C()
    >>> int(getProxiedObject(c) is c)
    1
    >>> p = ProxyBase(c)
    >>> int(getProxiedObject(p) is c)
    1
    >>> p2 = ProxyBase(p)
    >>> int(getProxiedObject(p2) is p)
    1

    """

def test_removeAllProxies():
    """
    >>> from zope.proxy import ProxyBase, removeAllProxies
    >>> class C:
    ...     pass
    >>> c = C()
    >>> int(removeAllProxies(c) is c)
    1
    >>> p = ProxyBase(c)
    >>> int(removeAllProxies(p) is c)
    1
    >>> p2 = ProxyBase(p)
    >>> int(removeAllProxies(p2) is c)
    1

    """

def test_queryProxy():
    """
    >>> from zope.proxy import ProxyBase, queryProxy
    >>> class P1(ProxyBase):
    ...    pass
    >>> class P2(ProxyBase):
    ...    pass
    >>> class C:
    ...     pass
    >>> c = C()
    >>> queryProxy(c, P1)
    >>> queryProxy(c, P1, 42)
    42
    >>> p1 = P1(c)
    >>> int(queryProxy(p1, P1) is p1)
    1
    >>> queryProxy(c, P2)
    >>> queryProxy(c, P2, 42)
    42
    >>> p2 = P2(p1)
    >>> int(queryProxy(p2, P1) is p1)
    1
    >>> int(queryProxy(p2, P2) is p2)
    1
    >>> int(queryProxy(p2, ProxyBase) is p2)
    1
    
    """

def test_queryInnerProxy():
    """
    >>> from zope.proxy import ProxyBase, queryProxy, queryInnerProxy
    >>> class P1(ProxyBase):
    ...    pass
    >>> class P2(ProxyBase):
    ...    pass
    >>> class C:
    ...     pass
    >>> c = C()
    >>> queryInnerProxy(c, P1)
    >>> queryInnerProxy(c, P1, 42)
    42
    >>> p1 = P1(c)
    >>> int(queryProxy(p1, P1) is p1)
    1
    >>> queryInnerProxy(c, P2)
    >>> queryInnerProxy(c, P2, 42)
    42
    >>> p2 = P2(p1)
    >>> int(queryInnerProxy(p2, P1) is p1)
    1
    >>> int(queryInnerProxy(p2, P2) is p2)
    1
    >>> int(queryInnerProxy(p2, ProxyBase) is p1)
    1

    >>> p3 = P1(p2)
    >>> int(queryProxy(p3, P1) is p3)
    1
    >>> int(queryInnerProxy(p3, P1) is p1)
    1
    >>> int(queryInnerProxy(p3, P2) is p2)
    1
    
    """

def test_sameProxiedObjects():
    """
    >>> from zope.proxy import ProxyBase, sameProxiedObjects
    >>> class C:
    ...     pass
    >>> c1 = C()
    >>> c2 = C()
    >>> int(sameProxiedObjects(c1, c1))
    1
    >>> int(sameProxiedObjects(ProxyBase(c1), c1))
    1
    >>> int(sameProxiedObjects(ProxyBase(c1), ProxyBase(c1)))
    1
    >>> int(sameProxiedObjects(ProxyBase(ProxyBase(c1)), c1))
    1
    >>> int(sameProxiedObjects(c1, ProxyBase(c1)))
    1
    >>> int(sameProxiedObjects(c1, ProxyBase(ProxyBase(c1))))
    1
    >>> int(sameProxiedObjects(c1, c2))
    0
    >>> int(sameProxiedObjects(ProxyBase(c1), c2))
    0
    >>> int(sameProxiedObjects(ProxyBase(c1), ProxyBase(c2)))
    0
    >>> int(sameProxiedObjects(ProxyBase(ProxyBase(c1)), c2))
    0
    >>> int(sameProxiedObjects(c1, ProxyBase(c2)))
    0
    >>> int(sameProxiedObjects(c1, ProxyBase(ProxyBase(c2))))
    0
    """


def test_suite():
    suite = unittest.makeSuite(ProxyTestCase)
    suite.addTest(DocTestSuite())
    return suite

if __name__ == "__main__":
    import sys
    runner = unittest.TextTestRunner(sys.stdout)
    result = runner.run(test_suite())
    newerrs = len(result.errors) + len(result.failures)
    sys.exit(newerrs and 1 or 0)
