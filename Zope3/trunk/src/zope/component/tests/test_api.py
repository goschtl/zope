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
import unittest, sys
from zope.interface import Interface
from zope.component.tests.request import Request
from zope.component.servicenames import Adapters


class I1(Interface): pass
class I2(Interface): pass
class I3(Interface): pass
class Comp:
    __implements__ = I2
    def __init__(self, context, request=None): self.context = context
class Comp2:
    __implements__ = I3
    def __init__(self, context, request=None): self.context = context

comp = Comp(1)

class Ob:
    __implements__ = I1

ob = Ob()


class R1(Interface): pass
class R12(Interface): pass
class R2(R1): pass
class R3(R2): pass
class R4(R3): pass

class P1(Interface): pass
class P2(P1): pass
class P3(P2): pass
class P4(P3): pass

class default_P3: pass
class any_P3: pass
class R2_P3: pass

from zope.component.tests.placelesssetup import PlacelessSetup

class Test(PlacelessSetup, unittest.TestCase):

    def testAdapter(self):
        from zope.component import getAdapter, getService, queryAdapter
        from zope.component.exceptions import ComponentLookupError

        # If an object implements the interface you want to adapt to,
        # getAdapter should simply return the object.
        self.assertEquals(getAdapter(ob, I1), ob)

        # If an adapter isn't registered for the given object and interface,
        # and you provide no default, raise ComponentLookupError...
        self.assertRaises(ComponentLookupError, getAdapter, ob, I2)

        # ...otherwise, you get the default
        self.assertEquals(queryAdapter(ob, I2, Test), Test)

        getService(None, Adapters).provideAdapter(I1, I2, Comp)
        c = getAdapter(ob, I2)
        self.assertEquals(c.__class__, Comp)
        self.assertEquals(c.context, ob)

    def testContextArgument(self):
        # Basically, the same tests as in testAdapter, but with the
        # 'context' argument given. As this is only testing the global
        # service, this is pretty much a no-operation.
        from zope.component import getAdapter, getService, queryAdapter
        from zope.component.exceptions import ComponentLookupError

        self.assertEquals(getAdapter(ob, I1, context=None), ob)
        self.assertEquals(getAdapter(ob, I1, context=ob), ob)

        # If an adapter isn't registered for the given object and interface,
        # and you provide no default, raise ComponentLookupError...
        self.assertRaises(ComponentLookupError, getAdapter, ob, I2,
                          context=ob)

        # ...otherwise, you get the default
        self.assertEquals(queryAdapter(ob, I2, Test, context=ob), Test)

        getService(None, Adapters).provideAdapter(I1, I2, Comp)
        c = getAdapter(ob, I2, context=ob)
        self.assertEquals(c.__class__, Comp)
        self.assertEquals(c.context, ob)

    def testNamedAdapter(self):

        self.testAdapter()

        from zope.component import getAdapter, getService, queryAdapter
        from zope.component.exceptions import ComponentLookupError

        # If an object implements the interface you want to adapt to,
        # getAdapter should simply return the object UNLESS we are asking for a
        # named adapter.
        self.assertRaises(ComponentLookupError, getAdapter, ob, I1, 'test')

        # If an adapter isn't registered for the given object and interface,
        # and you provide no default, raise ComponentLookupError...
        self.assertRaises(ComponentLookupError, getAdapter, ob, I2, 'test')

        # ...otherwise, you get the default
        self.assertEquals(queryAdapter(ob, I2, Test, name='test'), Test)

        class Comp2(Comp): pass

        getService(None, Adapters).provideAdapter(I1, I2, Comp2, name='test')
        c = getAdapter(ob, I2, name='test')
        self.assertEquals(c.__class__, Comp2)
        self.assertEquals(c.context, ob)

    def testMultipleAdapterFactories(self):
        from zope.component import getAdapter, getService

        # Basically, this represents a 2-stage adaptation. You can get
        # from I1 to I2 by way of adapter Comp adapting Comp2
        getService(None, Adapters).provideAdapter(I1, I2, [Comp2, Comp])
        c = getAdapter(ob, I2)
        self.assertEquals(c.__class__, Comp)
        self.assertEquals(c.context.context, ob)

    def testAdapterForInterfaceNone(self):
        from zope.component import getAdapter, getService

        # providing an adapter for None says that your adapter can
        # adapt anything to I2.
        getService(None, Adapters).provideAdapter(None, I2, Comp)
        c = getAdapter(ob, I2)
        self.assertEquals(c.__class__, Comp)
        self.assertEquals(c.context, ob)

    def testUtility(self):
        from zope.component import getUtility, queryUtility
        from zope.component import getService
        from zope.component.exceptions import ComponentLookupError

        self.assertRaises(ComponentLookupError, getUtility, ob, I1)
        self.assertRaises(ComponentLookupError, getUtility, ob, I2)
        self.assertEquals(queryUtility(ob, I2, Test), Test)

        getService(None, 'Utilities').provideUtility(I2, comp)
        self.assertEquals(id(getUtility(ob, I2)), id(comp))

    def testNamedUtility(self):
        from zope.component import getUtility, queryUtility
        from zope.component import getService
        from zope.component.exceptions import ComponentLookupError

        self.testUtility()

        self.assertRaises(ComponentLookupError, getUtility, ob, I1, 'test')
        self.assertRaises(ComponentLookupError, getUtility, ob, I2, 'test')
        self.assertEquals(queryUtility(ob, I2, Test, 'test'), Test)

        getService(None, 'Utilities').provideUtility(I2, comp, 'test')
        self.assertEquals(id(getUtility(ob, I2, 'test')), id(comp))

    def testView(self):
        from zope.component import getView, queryView, getService
        from zope.component.exceptions import ComponentLookupError

        self.assertRaises(ComponentLookupError,
                          getView, ob, 'foo', Request(I1))
        self.assertRaises(ComponentLookupError,
                          getView, ob, 'foo', Request(I2))
        self.assertEquals(queryView(ob, 'foo', Request(I2), Test), Test)

        getService(None, 'Views').provideView(I1, 'foo', I2, [Comp])
        c = getView(ob, 'foo', Request(I2))
        self.assertEquals(c.__class__, Comp)
        self.assertEquals(c.context, ob)

        self.assertRaises(ComponentLookupError,
                          getView, ob, 'foo2', Request(I1))
        self.assertRaises(ComponentLookupError,
                          getView, ob, 'foo2', Request(I2))
        self.assertEquals(queryView(ob, 'foo2', Request(I2), Test), Test)

        self.assertEquals(queryView(ob, 'foo2', Request(I1), None), None)

    def testViewWithContextArgument(self):
        # Basically the same as testView, but exercising the context
        # argument. As this only tests global views, the context
        # argument is pretty much a no-operation.
        from zope.component import getView, queryView, getService
        from zope.component.exceptions import ComponentLookupError

        self.assertRaises(ComponentLookupError,
                          getView, ob, 'foo', Request(I1), context=ob)
        self.assertRaises(ComponentLookupError,
                          getView, ob, 'foo', Request(I2), context=ob)
        self.assertEquals(queryView(ob, 'foo', Request(I2), Test, context=ob),
                          Test)

        getService(None, 'Views').provideView(I1, 'foo', I2, [Comp])
        c = getView(ob, 'foo', Request(I2), context=ob)
        self.assertEquals(c.__class__, Comp)
        self.assertEquals(c.context, ob)

        self.assertRaises(ComponentLookupError,
                          getView, ob, 'foo2', Request(I1), context=ob)
        self.assertRaises(ComponentLookupError,
                          getView, ob, 'foo2', Request(I2), context=ob)
        self.assertEquals(queryView(ob, 'foo2', Request(I2), Test,
                                    context=ob),
                          Test)

        self.assertEquals(queryView(ob, 'foo2', Request(I1), None,
                                    context=ob),
                          None)

    def testDefaultViewName(self):
        from zope.component import getService
        from zope.exceptions import NotFoundError
        viewService = getService(None, 'Views')
        self.assertRaises(NotFoundError,
                          viewService.getDefaultViewName,
                          ob, Request(I1))
        viewService.setDefaultViewName(I1, I2, 'sample_name')
        self.assertEquals(viewService.getDefaultViewName(ob, Request(I2)),
                          'sample_name')
        self.assertRaises(NotFoundError,
                          viewService.getDefaultViewName,
                          ob, Request(I1))

    # The following tests are copied from
    # Interface.Registry.tests.IAdapterRegistry

    def __registery(self):
        from zope.component.adapter import GlobalAdapterService

        registry = GlobalAdapterService()


        registry.provideAdapter(None, P3, [default_P3])
        registry.provideAdapter(Interface, P3, [any_P3])
        registry.provideAdapter(R2, P3, [R2_P3])

        return registry

    def test_getRegisteredMatching_all(self):
        registry = self.__registery()

        got = list(registry.getRegisteredMatching())
        got.sort()
        expect = [
            ('', None, P3, [default_P3]),
            ('', Interface, P3, [any_P3]),
            ('', R2, P3, [R2_P3]),
            ]
        expect.sort()
        self.assertEqual(got, expect)

    def test_getRegisteredMatching_for_R1(self):
        registry = self.__registery()

        got = list(registry.getRegisteredMatching(
            for_interfaces = (R1, )
            ))
        got.sort()
        expect = [
            ('', None, P3, [default_P3]),
            ('', Interface, P3, [any_P3]),
            ]
        expect.sort()
        self.assertEqual(got, expect)

    def test_getRegisteredMatching_for_multiple(self):
        registry = self.__registery()

        got = list(registry.getRegisteredMatching(
            for_interfaces = (R12, R2)
            ))
        got.sort()
        expect = [
            ('', None, P3, [default_P3]),
            ('', Interface, P3, [any_P3]),
            ('', R2, P3, [R2_P3]),
            ]
        expect.sort()
        self.assertEqual(got, expect)

    def test_getRegisteredMatching_provided_P1(self):
        registry = self.__registery()

        got = list(registry.getRegisteredMatching(
            provided_interfaces = (P1, )
            ))
        got.sort()
        expect = [
            ('', None, P3, [default_P3]),
            ('', Interface, P3, [any_P3]),
            ('', R2, P3, [R2_P3]),
            ]
        expect.sort()
        self.assertEqual(got, expect)

    def test_getRegisteredMatching_provided_P2(self):
        registry = self.__registery()

        got = list(registry.getRegisteredMatching(
            provided_interfaces = (P3, )
            ))
        got.sort()
        expect = [
            ('', None, P3, [default_P3]),
            ('', Interface, P3, [any_P3]),
            ('', R2, P3, [R2_P3]),
            ]
        expect.sort()
        self.assertEqual(got, expect)

    def test_getRegisteredMatching_for_and_provided_1(self):
        registry = self.__registery()

        got = list(registry.getRegisteredMatching(
            for_interfaces = (R4, R12),
            provided_interfaces = (P1, ),
            ))
        got.sort()
        expect = [
            ('', None, P3, [default_P3]),
            ('', Interface, P3, [any_P3]),
            ('', R2, P3, [R2_P3]),
            ]
        expect.sort()
        self.assertEqual(got, expect)

    def test_getRegisteredMatching_for_and_provided_2(self):
        registry = self.__registery()

        got = list(registry.getRegisteredMatching(
            for_interfaces = (R4, R12),
            provided_interfaces = (P3, ),
            ))
        got.sort()
        expect = [
            ('', None, P3, [default_P3]),
            ('', Interface, P3, [any_P3]),
            ('', R2, P3, [R2_P3]),
            ]
        expect.sort()
        self.assertEqual(got, expect)

    def test_getRegisteredMatching_for_and_provided_exact(self):
        registry = self.__registery()

        got = list(registry.getRegisteredMatching(
            for_interfaces = (R2, ),
            provided_interfaces = (P3, ),
            ))
        got.sort()
        expect = [
            ('', None, P3, [default_P3]),
            ('', Interface, P3, [any_P3]),
            ('', R2, P3, [R2_P3]),
            ]
        expect.sort()
        self.assertEqual(got, expect)

def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
