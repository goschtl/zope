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
import sys
import unittest

# Note that this is testing both that SimpleMethodWrapper works,
# and that SimpleMethodWrapper is available as
# from zope.proxy.context import Wrapper
#
# However, this test suite can form the basis of a test for the improved C
# implementation, when that lands.
#
from zope.proxy.context import \
        Wrapper, wrapperTypes, ContextMethod, \
        ContextProperty, ContextGetProperty, ContextSetProperty, \
        ContextSuper

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
    thisIsAContextGetProperty = ContextGetProperty(_getter, _setter)
    thisIsAContextSetProperty = ContextSetProperty(_getter, _setter)

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
    thisIsAContextGetProperty = ContextGetProperty(_getter, _setter)
    thisIsAContextSetProperty = ContextSetProperty(_getter, _setter)

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
    thisIsAContextGetProperty = ContextGetProperty(_getter)


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
        self.assert_(self.obj.result is self.wrapped)

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

    def testGetContextProperty(self):
        self.assertEqual(self.wrapped.thisIsAContextProperty, True)
        self.assert_(self.obj.result is self.wrapped)

    def testGetContextGetProperty(self):
        self.assertEqual(self.wrapped.thisIsAContextGetProperty, True)
        self.assert_(self.obj.result is self.wrapped)

    def testNotFound(self):
        self.assertRaises(AttributeError,
                          getattr, self.wrapped, 'noSuchAttribute')


class TestNewStyleClassWithSlots(TestClassicClass):

    _class = NewStyleClassWithSlots

    # Setting properties doesn't work with classic classes,
    # so this class has extra tests for setting properties in
    # new-style classes.

    def testSetContextProperty(self):
        value = 23
        self.wrapped.thisIsAContextProperty = value
        result_obj, result_value = self.obj.result
        self.assert_(result_obj is self.wrapped)
        self.assert_(result_value is value)

    def testSetContextGetProperty(self):
        value = 23
        self.wrapped.thisIsAContextGetProperty = value
        result_obj, result_value = self.obj.result
        self.assert_(result_obj is self.obj)
        self.assert_(result_value is value)

    def testGetContextSetProperty(self):
        self.assertEqual(self.wrapped.thisIsAContextSetProperty, True)
        self.assert_(self.obj.result is self.obj)

    def testSetContextSetProperty(self):
        value = 23
        self.wrapped.thisIsAContextSetProperty = value
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

class TestWrapperTypeSelection(unittest.TestCase):

    def testSelection(self):

        from zope.proxy.context \
            import SimpleMethodWrapper, SimpleCallableMethodWrapper, \
            SimpleGetitemMethodWrapper, SimpleCallableGetitemMethodWrapper

        self.assert_(type(Wrapper({})) is SimpleMethodWrapper)
        self.assert_(type(Wrapper(SimpleClass())) is SimpleMethodWrapper)
        self.assert_(type(Wrapper(CallableClass())) is
                     SimpleCallableMethodWrapper)
        self.assert_(type(Wrapper(ClassWithGetitem())) is
                     SimpleGetitemMethodWrapper)
        self.assert_(type(Wrapper(CallableClassWithGetitem())) is
                     SimpleCallableGetitemMethodWrapper)
        self.assert_(type(Wrapper(CallableGetitemNoContextMethods())) is
                     SimpleMethodWrapper)

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
        # let's just check that the (slightly broken) converse is true
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
        # let's just check that the (slightly broken) converse is true
        self.assert_(callable(wrapped))
        self.assertRaises(TypeError, wrapped)

        self.assert_(hasattr(obj, '__getitem__'))
        self.assert_(hasattr(wrapped, '__getitem__'))
        self.assertEqual(wrapped[0], 23)
        self.assertEqual(wrapped.__getitem__(0), 23)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestNewStyleClass),
        unittest.makeSuite(TestNewStyleClassWithSlots),
        unittest.makeSuite(TestClassicClass),
        unittest.makeSuite(TestWrapperTypeSelection),
        ))


if __name__ == "__main__":
    runner = unittest.TextTestRunner(sys.stdout)
    result = runner.run(test_suite())
    newerrs = len(result.errors) + len(result.failures)
    sys.exit(newerrs and 1 or 0)
