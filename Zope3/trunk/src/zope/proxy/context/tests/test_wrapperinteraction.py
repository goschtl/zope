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
"""Testing the interaction of Wrapper, ContextWrapper, ContextMethod etc.

Testing the Wrapper type's interaction with ContextDescriptors such as
ContextMethod and ContextProperty, and the ContextWrapper factory function
that creates a wrapper object, and checks for misuse of ContextDescriptors
as members of classic classes. (Descriptors generally don't work properly
as members of classic classes.)

$Id: test_wrapperinteraction.py,v 1.3 2003/04/09 11:44:27 philikon Exp $
"""
import sys
import unittest

from zope.proxy.context import Wrapper, ContextMethod, ContextProperty
from zope.proxy.context import ContextSuper, ContextWrapper, ContextAware

class NewStyleClass(object):

    result = None

    def thisIsAContextMethod(wrapped_self, val=None):
        wrapped_self.result = wrapped_self
        return val
    thisIsAContextMethod = ContextMethod(thisIsAContextMethod)

    def __call__(wrapped_self, a, b=None):
        wrapped_self.result = wrapped_self, a, b
        return a
    __call__ = ContextMethod(__call__)

    def __getitem__(wrapped_self, a, b=None):
        wrapped_self.result = wrapped_self, a, b
        return a
    __getitem__ = ContextMethod(__getitem__)

    def thisIsNotAContextMethod(self, val=None):
        self.result = self
        return val

    def _getter(wrapped_self):
        wrapped_self.result = wrapped_self
        return True

    def _setter(wrapped_self, value):
        wrapped_self.result = wrapped_self, value
    thisIsAContextProperty = ContextProperty(_getter, _setter)

    def this_is_any_old_method(self):
        return 'base', self

class NewStyleClassWithSlots(object):
    __slots__ = ['result']

    def __init__(self):
        self.result = None

    def thisIsAContextMethod(wrapped_self, val=None):
        wrapped_self.result = wrapped_self
        return val
    thisIsAContextMethod = ContextMethod(thisIsAContextMethod)

    def __call__(wrapped_self, a, b=None):
        wrapped_self.result = wrapped_self, a, b
        return a
    __call__ = ContextMethod(__call__)

    def __getitem__(wrapped_self, a, b=None):
        wrapped_self.result = wrapped_self, a, b
        return a
    __getitem__ = ContextMethod(__getitem__)

    def thisIsNotAContextMethod(self, val=None):
        self.result = self
        return val

    def _getter(wrapped_self):
        wrapped_self.result = wrapped_self
        return True

    def _setter(wrapped_self, value):
        wrapped_self.result = wrapped_self, value

    thisIsAContextProperty = ContextProperty(_getter, _setter)

    def this_is_any_old_method(self):
        return 'base', self


class ClassicClass:

    result = None

    def thisIsAContextMethod(wrapped_self, val=None):
        wrapped_self.result = wrapped_self
        return val
    thisIsAContextMethod = ContextMethod(thisIsAContextMethod)

    def __call__(wrapped_self, a, b=None):
        wrapped_self.result = wrapped_self, a, b
        return a
    __call__ = ContextMethod(__call__)

    def __getitem__(wrapped_self, a, b=None):
        wrapped_self.result = wrapped_self, a, b
        return a
    __getitem__ = ContextMethod(__getitem__)

    def thisIsNotAContextMethod(self, val=None):
        self.result = self
        return val

    def _getter(wrapped_self):
        wrapped_self.result = wrapped_self
        return True

    # not using a setter, as this is a classic class, and so
    # setting an attribute that is a property results in overwriting
    # that property.
    thisIsAContextProperty = ContextProperty(_getter)


class TestClassicClass(unittest.TestCase):

    _class = ClassicClass

    def createObject(self):
        # to be overridden in tests that subclass this one
        return self._class()

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.obj = self.createObject()
        self.wrapped = Wrapper(self.obj)
        self.assertEqual(self.obj.result, None)

    def testContextMethod(self):
        value = object()
        self.assertEqual(self.wrapped.thisIsAContextMethod(value), value)
        # ContextMethod doesn't work with classic classes
        self.assert_(self.obj.result is self.obj)

        self.assertEqual(self.obj.thisIsAContextMethod(value), value)
        self.assert_(self.obj.result is self.obj)

    def testNotContextMethod(self):
        value = object()
        self.assertEqual(self.wrapped.thisIsNotAContextMethod(value), value)
        self.assert_(self.obj.result is self.obj)

    def testCall(self):
        value_a = object()
        value_b = object()

        self.assertRaises(TypeError, self.wrapped)

        self.assertEqual(self.wrapped(value_a), value_a)
        result_obj, result_a, result_b = self.obj.result
        # ContextMethod doesn't work with classic class
        self.assert_(result_obj is self.obj)
        self.assert_(result_a is value_a)
        self.assert_(result_b is None)

        self.assertEqual(self.wrapped(value_a, value_b), value_a)
        result_obj, result_a, result_b = self.obj.result
        # ContextMethod doesn't work with classic class
        self.assert_(result_obj is self.obj)
        self.assert_(result_a is value_a)
        self.assert_(result_b is value_b)

        self.assertEqual(self.wrapped(value_a, b=value_b), value_a)
        result_obj, result_a, result_b = self.obj.result
        # ContextMethod doesn't work with classic class
        self.assert_(result_obj is self.obj)
        self.assert_(result_a is value_a)
        self.assert_(result_b is value_b)

        self.assertEqual(self.wrapped(a=value_a, b=value_b), value_a)
        result_obj, result_a, result_b = self.obj.result
        # ContextMethod doesn't work with classic class
        self.assert_(result_obj is self.obj)
        self.assert_(result_a is value_a)
        self.assert_(result_b is value_b)

    def testGetitem(self):
        value_a = object()
        value_b = object()

        self.assertRaises(TypeError, self.wrapped)

        self.assertEqual(self.wrapped[value_a], value_a)
        result_obj, result_a, result_b = self.obj.result
        # ContextMethod doesn't work with classic class
        self.assert_(result_obj is self.obj)
        self.assert_(result_a is value_a)
        self.assert_(result_b is None)

        self.assertEqual(self.wrapped.__getitem__(value_a, value_b), value_a)
        result_obj, result_a, result_b = self.obj.result

        # context wrapping doesn't work for classic classes
        self.assert_(result_obj is self.obj)
        self.assert_(result_a is value_a)
        self.assert_(result_b is value_b)

        self.assertEqual(self.wrapped.__getitem__(value_a, b=value_b), value_a)
        result_obj, result_a, result_b = self.obj.result
        self.assert_(result_obj is self.obj)
        self.assert_(result_a is value_a)
        self.assert_(result_b is value_b)

        self.assertEqual(self.wrapped.__getitem__(a=value_a, b=value_b),
                         value_a)
        result_obj, result_a, result_b = self.obj.result
        self.assert_(result_obj is self.obj)
        self.assert_(result_a is value_a)
        self.assert_(result_b is value_b)

    def testGetContextProperty(self):
        self.assertEqual(self.wrapped.thisIsAContextProperty, True)
        # context properties don't work with classic classes
        self.assert_(self.obj.result is self.obj)

    def testNotFound(self):
        self.assertRaises(AttributeError,
                          getattr, self.wrapped, 'noSuchAttribute')


class TestNewStyleClassWithSlots(TestClassicClass):

    _class = NewStyleClassWithSlots

    # Setting properties doesn't work with classic classes,
    # so this class has extra tests for setting properties in
    # new-style classes.

    def testCall(self):
        value_a = object()
        value_b = object()

        self.assertRaises(TypeError, self.wrapped)

        self.assertEqual(self.wrapped(value_a), value_a)
        result_obj, result_a, result_b = self.obj.result
        self.assert_(result_obj is self.wrapped)
        self.assert_(result_a is value_a)
        self.assert_(result_b is None)

        self.assertEqual(self.wrapped(value_a, value_b), value_a)
        result_obj, result_a, result_b = self.obj.result
        self.assert_(result_obj is self.wrapped)
        self.assert_(result_a is value_a)
        self.assert_(result_b is value_b)

        self.assertEqual(self.wrapped(value_a, b=value_b), value_a)
        result_obj, result_a, result_b = self.obj.result
        self.assert_(result_obj is self.wrapped)
        self.assert_(result_a is value_a)
        self.assert_(result_b is value_b)

        self.assertEqual(self.wrapped(a=value_a, b=value_b), value_a)
        result_obj, result_a, result_b = self.obj.result
        self.assert_(result_obj is self.wrapped)
        self.assert_(result_a is value_a)
        self.assert_(result_b is value_b)

    def testGetitem(self):
        value_a = object()
        value_b = object()

        self.assertRaises(TypeError, self.wrapped)

        self.assertEqual(self.wrapped[value_a], value_a)
        result_obj, result_a, result_b = self.obj.result
        self.assert_(result_obj is self.wrapped)
        self.assert_(result_a is value_a)
        self.assert_(result_b is None)

        self.assertEqual(self.wrapped.__getitem__(value_a, value_b), value_a)
        result_obj, result_a, result_b = self.obj.result
        self.assert_(result_obj is self.wrapped)
        self.assert_(result_a is value_a)
        self.assert_(result_b is value_b)

        self.assertEqual(self.wrapped.__getitem__(value_a, b=value_b), value_a)
        result_obj, result_a, result_b = self.obj.result
        self.assert_(result_obj is self.wrapped)
        self.assert_(result_a is value_a)
        self.assert_(result_b is value_b)

        self.assertEqual(self.wrapped.__getitem__(a=value_a, b=value_b),
                         value_a)
        result_obj, result_a, result_b = self.obj.result
        self.assert_(result_obj is self.wrapped)
        self.assert_(result_a is value_a)
        self.assert_(result_b is value_b)

    def testContextMethod(self):
        value = object()
        self.assertEqual(self.wrapped.thisIsAContextMethod(value), value)
        self.assert_(self.obj.result is self.wrapped)

        self.assertEqual(self.obj.thisIsAContextMethod(value), value)
        self.assert_(self.obj.result is self.obj)

    def testGetContextProperty(self):
        self.assertEqual(self.wrapped.thisIsAContextProperty, True)
        self.assert_(self.obj.result is self.wrapped)

    def testSetContextProperty(self):
        value = 23
        self.wrapped.thisIsAContextProperty = value
        result_obj, result_value = self.obj.result
        self.assert_(result_obj is self.wrapped)
        self.assert_(result_value is value)

    def testContextSuper(self):

        def this_is_any_old_method(self):
            return 'sub', self

        Sub = type('sub', (self._class, ), {
            'this_is_any_old_method': this_is_any_old_method,
            })

        inst = Wrapper(Sub())
        name, rinst = inst.this_is_any_old_method()
        self.assertEqual(name,  'sub')
        self.assert_(rinst is not inst)

        name, rinst = ContextSuper(Sub, inst).this_is_any_old_method()
        self.assertEqual(name,  'base')
        self.assert_(rinst is inst)


class TestNewStyleClass(TestNewStyleClassWithSlots):

    _class = NewStyleClass

    def testGetContextProperty_w_name_in_dict(self):
        self.obj.__dict__['thisIsAContextProperty'] = False
        self.assertEqual(self.obj.thisIsAContextProperty, True)
        self.assert_(self.obj.result is self.obj)
        self.assertEqual(self.wrapped.thisIsAContextProperty, True)
        self.assert_(self.obj.result is self.wrapped)

    def testSetContextProperty_w_name_in_dict(self):
        self.obj.__dict__['thisIsAContextProperty'] = False
        value = 23
        self.obj.thisIsAContextProperty = value
        result_obj, result_value = self.obj.result
        self.assert_(result_obj is self.obj)
        self.assert_(result_value is value)

        self.wrapped.thisIsAContextProperty = value
        result_obj, result_value = self.wrapped.result
        self.assert_(result_obj is self.wrapped)
        self.assert_(result_value is value)


class SimpleClass(object):
    pass

class CallableClass(object):
    called = False
    def __call__(self):
        self.called = True
    __call__ = ContextMethod(__call__)

class ClassWithGetitem(object):
    gotitem = False
    def __getitem__(self, key):
        self.gotitem = True
        return key*2
    __getitem__ = ContextMethod(__getitem__)

class CallableClassWithGetitem(CallableClass, ClassWithGetitem):
    pass

class CallableGetitemNoContextMethods:
    def __call__(self):
        pass
    def __getitem__(self, key):
        pass

class TestWrapperOnObjectsWithDifferentSlots(unittest.TestCase):

    def testSimpleClass(self):
        obj = SimpleClass()
        wrapped = Wrapper(obj)
        self.assertRaises(TypeError, obj)  # call as obj()
        self.assertRaises(TypeError, wrapped) # call as wrapped()
        self.assertRaises(TypeError, lambda: wrapped[23])
        self.assert_(not callable(obj))
        # This fails, because the base proxy c class in zope/proxy/proxy.c
        # fills the tp_call slot.
        #
        # self.assert_(not callable(wrapped))
        #
        # let's just check that the (slightly broken) converse is true
        self.assert_(callable(wrapped))

    def testCallableClass(self):
        obj = CallableClass()
        wrapped = Wrapper(obj)
        self.assert_(callable(obj))
        self.assert_(callable(wrapped))
        wrapped()
        self.assertEqual(obj.called, True)

        self.assertRaises(TypeError, lambda: wrapped[23])
        self.assertRaises(AttributeError, getattr, wrapped, '__getitem__')

    def testGetitemClass(self):
        obj = ClassWithGetitem()
        wrapped = Wrapper(obj)
        self.assert_(not callable(obj))
        # This fails, because the base proxy c class in zope/proxy/proxy.c
        # fills the tp_call slot.
        #
        # self.assert_(not callable(wrapped))
        #
        # let's just check that the converse is true
        self.assert_(callable(wrapped))
        self.assertRaises(TypeError, wrapped)

        self.assert_(hasattr(obj, '__getitem__'))
        self.assert_(hasattr(wrapped, '__getitem__'))
        self.assertEqual(wrapped[23], 46)
        self.assertEqual(wrapped.__getitem__(23), 46)

    def testCallableGetitemClass(self):
        obj = CallableClassWithGetitem()
        wrapped = Wrapper(obj)
        self.assert_(callable(obj))
        self.assert_(callable(wrapped))
        wrapped()
        self.assertEqual(obj.called, True)

        self.assert_(hasattr(obj, '__getitem__'))
        self.assert_(hasattr(wrapped, '__getitem__'))
        self.assertEqual(wrapped[23], 46)
        self.assertEqual(wrapped.__getitem__(23), 46)

    def testBuiltinMethod(self):
        obj = {0:23}
        wrapped = Wrapper(obj)
        self.assert_(not callable(obj))
        # This fails, because the base proxy c class in zope/proxy/proxy.c
        # fills the tp_call slot.
        #
        # self.assert_(not callable(wrapped))
        #
        # let's just check that the converse is true
        self.assert_(callable(wrapped))
        self.assertRaises(TypeError, wrapped)

        self.assert_(hasattr(obj, '__getitem__'))
        self.assert_(hasattr(wrapped, '__getitem__'))
        self.assertEqual(wrapped[0], 23)
        self.assertEqual(wrapped.__getitem__(0), 23)

class TestContextWrapperFactory(unittest.TestCase):

    pass

# XXX commented this test out because of Jim's change in
# src/zope/proxy/context/__init__.py

##     def testClassicClassWarning(self):
##         from types import ClassType
##         class Classic:
##             __metaclass__ = ClassType
##             def foo(self):
##                 pass

##         class BadClassic:
##             __metaclass__ = ClassType
##             def foo(self):
##                 pass
##             foo = ContextMethod(foo)

##         # ok if there are no ContextDescriptors 
##         w = ContextWrapper(Classic(), None)

##         # raises if there is a ContextDescriptor
##         self.assertRaises(TypeError, ContextWrapper, BadClassic(), None)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestNewStyleClass),
        unittest.makeSuite(TestNewStyleClassWithSlots),
        unittest.makeSuite(TestClassicClass),
        unittest.makeSuite(TestWrapperOnObjectsWithDifferentSlots),
        unittest.makeSuite(TestContextWrapperFactory),
        ))


if __name__ == "__main__":
    runner = unittest.TextTestRunner(sys.stdout)
    result = runner.run(test_suite())
    newerrs = len(result.errors) + len(result.failures)
    sys.exit(newerrs and 1 or 0)
