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

import unittest

from zope.component import servicenames
from zope.component import getAdapter, queryAdapter
from zope.component import getNamedAdapter, queryNamedAdapter
from zope.component import getService
from zope.component import getUtility, queryUtility
from zope.component import getDefaultViewName
from zope.component import queryMultiAdapter
from zope.component.exceptions import ComponentLookupError
from zope.component.servicenames import Adapters
from zope.component.tests.placelesssetup import PlacelessSetup
from zope.component.tests.request import Request

from zope.interface import Interface, implements

class I1(Interface):
    pass
class I2(Interface):
    pass
class I3(Interface):
    pass

class Comp:
    implements(I2)
    def __init__(self, context, request=None): self.context = context

class Comp2:
    implements(I3)
    def __init__(self, context, request=None): self.context = context

comp = Comp(1)

class Ob:
    implements(I1)

ob = Ob()

class Conforming(Ob):
    def __conform__(self, i):
        if i is I3:
            return Comp(self)


class Test(PlacelessSetup, unittest.TestCase):

    def testAdapter_via_conform(self):

        ob = Conforming()

        # If an object implements the interface you want to adapt to,
        # getAdapter should simply return the object.
        self.assertEquals(getAdapter(ob, I1), ob)

        # If an adapter isn't registered for the given object and interface,
        # and you provide no default, raise ComponentLookupError...
        self.assertRaises(ComponentLookupError, getAdapter, ob, I2)

        # If an adapter isn't registered for the given object and interface,
        # and you provide no default, raise ComponentLookupError...
        self.assertRaises(ComponentLookupError, getAdapter, Conforming, I2)

        # ...otherwise, you get the default
        self.assertEquals(queryAdapter(ob, I2, Test), Test)

        # ...otherwise, you get the default
        self.assertEquals(queryAdapter(Conforming, I2, Test), Test)

        # ...otherwise, you get the default
        self.assertEquals(queryAdapter(Conforming, I3, Test), Test)

        getService(None, Adapters).register([I1], I2, '', Comp)
        c = getAdapter(ob, I2)
        self.assertEquals(c.__class__, Comp)
        self.assertEquals(c.context, ob)

        c = getAdapter(ob, I3)
        self.assertEquals(c.__class__, Comp)
        self.assertEquals(c.context, ob)

    def testAdapter(self):
        # If an object implements the interface you want to adapt to,
        # getAdapter should simply return the object.
        self.assertEquals(getAdapter(ob, I1), ob)

        # If an adapter isn't registered for the given object and interface,
        # and you provide no default, raise ComponentLookupError...
        self.assertRaises(ComponentLookupError, getAdapter, ob, I2)

        # ...otherwise, you get the default
        self.assertEquals(queryAdapter(ob, I2, Test), Test)

        getService(None, Adapters).register([I1], I2, '', Comp)
        c = getAdapter(ob, I2)
        self.assertEquals(c.__class__, Comp)
        self.assertEquals(c.context, ob)

    def testInterfaceCall(self):
        getService(None, Adapters).register([I1], I2, '', Comp)
        c = I2(ob)
        self.assertEquals(c.__class__, Comp)
        self.assertEquals(c.context, ob)

    def testContextArgument(self):
        # Basically, the same tests as in testAdapter, but with the
        # 'context' argument given. As this is only testing the global
        # service, this is pretty much a no-operation.

        self.assertEquals(getAdapter(ob, I1, context=None), ob)
        self.assertEquals(getAdapter(ob, I1, context=ob), ob)

        # If an adapter isn't registered for the given object and interface,
        # and you provide no default, raise ComponentLookupError...
        self.assertRaises(ComponentLookupError, getAdapter, ob, I2,
                          context=ob)

        # ...otherwise, you get the default
        self.assertEquals(queryAdapter(ob, I2, Test, context=ob), Test)

        getService(None, Adapters).register([I1], I2, '', Comp)
        c = getAdapter(ob, I2, context=ob)
        self.assertEquals(c.__class__, Comp)
        self.assertEquals(c.context, ob)

    def testNamedAdapter(self):

        self.testAdapter()

        # If an object implements the interface you want to adapt to,
        # getAdapter should simply return the object UNLESS we are asking for a
        # named adapter.
        self.assertRaises(ComponentLookupError,
                          getNamedAdapter, ob, I1, 'test')

        # If an adapter isn't registered for the given object and interface,
        # and you provide no default, raise ComponentLookupError...
        self.assertRaises(ComponentLookupError,
                          getNamedAdapter, ob, I2, 'test')

        # ...otherwise, you get the default
        self.assertEquals(queryNamedAdapter(ob, I2, 'test', Test), Test)

        class Comp2(Comp): pass

        getService(None, Adapters).register([I1], I2, 'test', Comp2)
        c = getNamedAdapter(ob, I2, 'test')
        self.assertEquals(c.__class__, Comp2)
        self.assertEquals(c.context, ob)

    def testQueryMultiAdapter(self):
        # Adapting a combination of 2 objects to an interface
        class DoubleAdapter:
            implements(I3)
            def __init__(self, first, second):
                self.first = first
                self.second = second
        class Ob2:
            implements(I2)
        ob2 = Ob2()
        context = None
        getService(context, Adapters).register([I1, I2], I3, '', DoubleAdapter)
        c = queryMultiAdapter((ob, ob2), I3, context=context)
        self.assertEquals(c.__class__, DoubleAdapter)
        self.assertEquals(c.first, ob)
        self.assertEquals(c.second, ob2)

    def testAdapterForInterfaceNone(self):

        # providing an adapter for None says that your adapter can
        # adapt anything to I2.
        getService(None, Adapters).register([None], I2, '', Comp)
        c = getAdapter(ob, I2)
        self.assertEquals(c.__class__, Comp)
        self.assertEquals(c.context, ob)

    def testUtility(self):

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

        getService(None, servicenames.Presentation).provideView(
            I1, 'foo', I2, Comp)
        c = getView(ob, 'foo', Request(I2))
        self.assertEquals(c.__class__, Comp)
        self.assertEquals(c.context, ob)

        self.assertRaises(ComponentLookupError,
                          getView, ob, 'foo2', Request(I1))
        self.assertRaises(ComponentLookupError,
                          getView, ob, 'foo2', Request(I2))
        self.assertEquals(queryView(ob, 'foo2', Request(I2), Test), Test)

        self.assertEquals(queryView(ob, 'foo2', Request(I1), None), None)

    def testView_w_provided(self):
        from zope.component import getView, queryView, getService
        from zope.component.exceptions import ComponentLookupError

        self.assertRaises(ComponentLookupError,
                          getView, ob, 'foo', Request(I1), providing=I3)
        self.assertRaises(ComponentLookupError,
                          getView, ob, 'foo', Request(I2), providing=I3)
        self.assertEquals(
            queryView(ob, 'foo', Request(I2), Test, providing=I3),
            Test)

        getService(None, servicenames.Presentation).provideView(
            I1, 'foo', I2, Comp)

        self.assertRaises(ComponentLookupError,
                          getView, ob, 'foo', Request(I1), providing=I3)
        self.assertRaises(ComponentLookupError,
                          getView, ob, 'foo', Request(I2), providing=I3)
        self.assertEquals(
            queryView(ob, 'foo', Request(I2), Test, providing=I3),
            Test)


        getService(None, servicenames.Presentation).provideView(
            I1, 'foo', I2, Comp, providing=I3)

        c = getView(ob, 'foo', Request(I2), providing=I3)
        self.assertEquals(c.__class__, Comp)
        self.assertEquals(c.context, ob)

    def testMultiView(self):
        from zope.component import queryMultiView, getService
        from zope.component.exceptions import ComponentLookupError

        class Ob2:
            implements(I2)

        ob2 = Ob2()

        class IRequest(Interface):
            pass

        request = Request(IRequest)

        class MV:
            implements(I3)
            def __init__(self, context, other, request):
               self.context, self.other, self.request = context, other, request

        self.assertEquals(
            queryMultiView((ob, ob2), request, I3, 'foo', 42), 42)

        getService(None, servicenames.Presentation).provideAdapter(
            IRequest, MV, 'foo', (I1, I2), I3)

        view = queryMultiView((ob, ob2), request, I3, 'foo')
        self.assertEquals(view.__class__, MV)
        self.assertEquals(view.context, ob)
        self.assertEquals(view.other, ob2)
        self.assertEquals(view.request, request)

    def test_viewProvidingFunctions(self):        
        # Confirm that a call to getViewProving/queryViewProviding simply 
        # passes its arguments through to getView/queryView - here we hack
        # getView and queryView to inspect the args passed through.
        import zope.component

        # hack zope.component.getView
        def getView(object, name, request, context, providing):
            self.args = [object, name, request, context, providing]
        savedGetView = zope.component.getView
        zope.component.getView = getView

        # confirm pass through of args to getView by way of getViewProviding
        zope.component.getViewProviding(
            object='object', providing='providing', request='request', 
            context='context')
        self.assertEquals(self.args, 
            ['object', '', 'request', 'context', 'providing'])

        # hack zope.component.queryView
        def queryView(object, name, request, default, context, providing):
            self.args = [object, name, request, default, context, providing]
        savedQueryView = zope.component.queryView
        zope.component.queryView = queryView

        # confirm pass through of args to queryView by way of queryViewProviding 
        zope.component.queryViewProviding(
            object='object', providing='providing', request='request', 
            default='default', context='context')
        self.assertEquals(self.args, 
            ['object', '', 'request', 'default', 'context', 'providing'])

        # restore zope.component
        zope.component.getView = savedGetView
        zope.component.queryView = savedQueryView

    def testResource(self):

        from zope.component import getResource, queryResource, getService
        from zope.component.exceptions import ComponentLookupError

        r1 = Request(I1)
        r2 = Request(I2)

        self.assertRaises(ComponentLookupError, getResource, ob, 'foo', r1)
        self.assertRaises(ComponentLookupError, getResource, ob, 'foo', r2)
        self.assertEquals(queryResource(ob, 'foo', r2, Test), Test)

        getService(None, servicenames.Presentation).provideResource(
            'foo', I2, Comp)
        c = getResource(ob, 'foo', r2)
        self.assertEquals(c.__class__, Comp)
        self.assertEquals(c.context, r2)

        self.assertRaises(ComponentLookupError, getResource, ob, 'foo2', r1)
        self.assertRaises(ComponentLookupError, getResource, ob, 'foo2', r2)
        self.assertEquals(queryResource(ob, 'foo2', r2, Test), Test)

        self.assertEquals(queryResource(ob, 'foo2', r1, None), None)

    def testResource_w_provided(self):
        from zope.component import getResource, queryResource, getService
        from zope.component.exceptions import ComponentLookupError

        r1 = Request(I1)
        r2 = Request(I2)

        self.assertRaises(ComponentLookupError,
                          getResource, ob, 'foo', r1, providing=I3)
        self.assertRaises(ComponentLookupError,
                          getResource, ob, 'foo', r2, providing=I3)
        self.assertEquals(queryResource(ob, 'foo', r2, Test, providing=I3),
                          Test)

        getService(None, servicenames.Presentation).provideResource(
            'foo', I2, Comp)

        self.assertRaises(ComponentLookupError,
                          getResource, ob, 'foo', r1, providing=I3)
        self.assertRaises(ComponentLookupError,
                          getResource, ob, 'foo', r2, providing=I3)
        self.assertEquals(queryResource(ob, 'foo', r2, Test, providing=I3),
                          Test)


        getService(None, servicenames.Presentation).provideResource(
            'foo', I2, Comp, providing=I3)

        c = getResource(ob, 'foo', r2, providing=I3)
        self.assertEquals(c.__class__, Comp)
        self.assertEquals(c.context, r2)

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

        getService(None, servicenames.Presentation).provideView(
            I1, 'foo', I2, Comp)
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
        viewService = getService(None, servicenames.Presentation)
        self.assertRaises(NotFoundError,
                          getDefaultViewName,
                          ob, Request(I1))
        viewService.setDefaultViewName(I1, I2, 'sample_name')
        self.assertEquals(getDefaultViewName(ob, Request(I2)),
                          'sample_name')
        self.assertRaises(NotFoundError,
                          getDefaultViewName,
                          ob, Request(I1))


class TestNoSetup(unittest.TestCase):

    def testNotBrokenWhenNoService(self):
        self.assertRaises(TypeError, I2, ob)
        self.assertEquals(I2(ob, 42), 42)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test),
        unittest.makeSuite(TestNoSetup),
        ))

if __name__ == "__main__":
    unittest.TextTestRunner().run(test_suite())
