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
"""Tests for ZCML directives.
"""
import unittest

from zope.component.testing import PlacelessSetup


class Test_handler(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from zope.component.zcml import handler
        return handler(*args, **kw)

    def test_uses_configured_site_manager(self):
        from zope.component import getSiteManager
        from zope.component.testfiles.components import comp, IApp
        from zope.interface.registry import Components

        registry = Components()
        def dummy(context=None):
            return registry
        getSiteManager.sethook(dummy)

        try:
            self._callFUT('registerUtility', comp, IApp, u'')
            self.assertTrue(registry.getUtility(IApp) is comp)
        finally:
            getSiteManager.reset()


class Test__rolledUpFactory(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from zope.component.zcml import _rolledUpFactory
        return _rolledUpFactory(*args, **kw)

    def test_with_one(self):
        _OBJ = object()
        _CREATED = object()
        def _factory(obj):
            return _CREATED
        rolled = self._callFUT([_factory])
        self.assertTrue(rolled.factory is _factory)
        self.assertTrue(rolled(_OBJ) is _CREATED)

    def test_with_multiple(self):
        _OBJ = object()
        _CREATED1 = object()
        _CREATED2 = object()
        _CREATED3 = object()
        def _factory1(obj):
            return _CREATED1
        def _factory2(obj):
            return _CREATED2
        def _factory3(obj):
            return _CREATED3
        rolled = self._callFUT([_factory1, _factory2, _factory3])
        self.assertTrue(rolled.factory is _factory1)
        self.assertTrue(rolled(_OBJ) is _CREATED3)


class Test_adapter(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from zope.component.zcml import adapter
        return adapter(*args, **kw)

    def _makeConfigContext(self):
        class _Context(object):
            info = 'TESTING'
            def __init__(self):
                self._actions = []
            def action(self, *args, **kw):
                self._actions.append((args, kw))
        return _Context()
 
    def test_empty_factory(self):
        from zope.interface import Interface
        class IFoo(Interface):
            pass
        _cfg_ctx = self._makeConfigContext()
        self.assertRaises(ValueError,
                          self._callFUT, _cfg_ctx, [], [Interface], IFoo)
 
    def test_multiple_factory_multiple_for_(self):
        from zope.interface import Interface
        class IFoo(Interface):
            pass
        class IBar(Interface):
            pass
        class Foo(object):
            pass
        class Bar(object):
            pass
        _cfg_ctx = self._makeConfigContext()
        self.assertRaises(ValueError,
                          self._callFUT, _cfg_ctx, [Foo, Bar],
                                         [Interface, IBar], IFoo)

    def test_no_for__factory_not_adapts(self):
        #@adapter(IFoo)
        class _Factory(object):
            def __init__(self, context):
                self.context = context
        _cfg_ctx = self._makeConfigContext()
        self.assertRaises(TypeError, self._callFUT, _cfg_ctx, [_Factory])
 
    def test_no_for__factory_adapts_no_provides_factory_not_implements(self):
        from zope.interface import Interface
        from zope.component._declaration import adapter
        @adapter(Interface)
        class _Factory(object):
            def __init__(self, context):
                self.context = context
        _cfg_ctx = self._makeConfigContext()
        self.assertRaises(TypeError, self._callFUT, _cfg_ctx, [_Factory])
 
    def test_multiple_factory_single_for_(self):
        from zope.interface import Interface
        from zope.component.interface import provideInterface
        from zope.component.zcml import handler
        class IFoo(Interface):
            pass
        class Foo(object):
            pass
        class Bar(object):
            pass
        _cfg_ctx = self._makeConfigContext()
        self._callFUT(_cfg_ctx, [Foo, Bar], IFoo, [Interface])
        self.assertEqual(len(_cfg_ctx._actions), 3)
        self.assertEqual(_cfg_ctx._actions[0][0], ())
        # Register the adapter
        action =_cfg_ctx._actions[0][1]
        self.assertEqual(action['callable'], handler)
        self.assertEqual(action['discriminator'],
                         ('adapter', (Interface,), IFoo, ''))
        self.assertEqual(action['args'][0], 'registerAdapter')
        self.assertEqual(action['args'][1].factory, Foo) #rolled up
        self.assertEqual(action['args'][2], (Interface,))
        self.assertEqual(action['args'][3], IFoo)
        self.assertEqual(action['args'][4], '')
        self.assertEqual(action['args'][5], 'TESTING')
        # Register the provided interface
        self.assertEqual(_cfg_ctx._actions[1][0], ())
        action =_cfg_ctx._actions[1][1]
        self.assertEqual(action['callable'], provideInterface)
        self.assertEqual(action['discriminator'], None)
        self.assertEqual(action['args'], ('', IFoo))
        # Register the required interface(s)
        self.assertEqual(_cfg_ctx._actions[2][0], ())
        action =_cfg_ctx._actions[2][1]
        self.assertEqual(action['callable'], provideInterface)
        self.assertEqual(action['discriminator'], None)
        self.assertEqual(action['args'], ('', Interface))
 
    def test_single_factory_single_for_w_permission(self):
        from zope.interface import Interface
        from zope.security.adapter import LocatingUntrustedAdapterFactory
        from zope.component.zcml import handler
        class IFoo(Interface):
            pass
        class Foo(object):
            pass
        _cfg_ctx = self._makeConfigContext()
        self._callFUT(_cfg_ctx, [Foo], IFoo, [Interface], permission='testing')
        self.assertEqual(len(_cfg_ctx._actions), 3)
        self.assertEqual(_cfg_ctx._actions[0][0], ())
        # Register the adapter
        action =_cfg_ctx._actions[0][1]
        self.assertEqual(action['callable'], handler)
        self.assertEqual(action['discriminator'],
                         ('adapter', (Interface,), IFoo, ''))
        self.assertEqual(action['args'][0], 'registerAdapter')
        factory_proxy = action['args'][1]
        # Foo wraped by 'protected_factory' plus
        # 'LocatingUntrustedAdapterFactory'
        self.assertTrue(isinstance(factory_proxy,
                        LocatingUntrustedAdapterFactory))
        self.assertTrue(factory_proxy.factory.factory is Foo)
        self.assertEqual(action['args'][2], (Interface,))
        self.assertEqual(action['args'][3], IFoo)
        self.assertEqual(action['args'][4], '')
        self.assertEqual(action['args'][5], 'TESTING')
 
    def test_single_factory_single_for_w_locate_no_permission(self):
        from zope.interface import Interface
        from zope.security.adapter import LocatingUntrustedAdapterFactory
        from zope.component.zcml import handler
        class IFoo(Interface):
            pass
        class Foo(object):
            pass
        _cfg_ctx = self._makeConfigContext()
        self._callFUT(_cfg_ctx, [Foo], IFoo, [Interface], locate=True)
        self.assertEqual(len(_cfg_ctx._actions), 3)
        self.assertEqual(_cfg_ctx._actions[0][0], ())
        # Register the adapter
        action =_cfg_ctx._actions[0][1]
        self.assertEqual(action['callable'], handler)
        self.assertEqual(action['discriminator'],
                         ('adapter', (Interface,), IFoo, ''))
        self.assertEqual(action['args'][0], 'registerAdapter')
        factory_proxy = action['args'][1]
        # Foo wraped by 'LocatingUntrustedAdapterFactory'
        self.assertTrue(isinstance(factory_proxy,
                        LocatingUntrustedAdapterFactory))
        self.assertTrue(factory_proxy.factory is Foo)
        self.assertEqual(action['args'][2], (Interface,))
        self.assertEqual(action['args'][3], IFoo)
        self.assertEqual(action['args'][4], '')
        self.assertEqual(action['args'][5], 'TESTING')
 
    def test_single_factory_single_for_w_trusted_no_permission(self):
        from zope.interface import Interface
        from zope.security.adapter import TrustedAdapterFactory
        from zope.component.zcml import handler
        class IFoo(Interface):
            pass
        class Foo(object):
            pass
        _cfg_ctx = self._makeConfigContext()
        self._callFUT(_cfg_ctx, [Foo], IFoo, [Interface], trusted=True)
        self.assertEqual(len(_cfg_ctx._actions), 3)
        self.assertEqual(_cfg_ctx._actions[0][0], ())
        # Register the adapter
        action =_cfg_ctx._actions[0][1]
        self.assertEqual(action['callable'], handler)
        self.assertEqual(action['discriminator'],
                         ('adapter', (Interface,), IFoo, ''))
        self.assertEqual(action['args'][0], 'registerAdapter')
        factory_proxy = action['args'][1]
        # Foo wraped by 'LocatingUntrustedAdapterFactory'
        self.assertTrue(isinstance(factory_proxy, TrustedAdapterFactory))
        self.assertTrue(factory_proxy.factory is Foo)
        self.assertEqual(action['args'][2], (Interface,))
        self.assertEqual(action['args'][3], IFoo)
        self.assertEqual(action['args'][4], '')
        self.assertEqual(action['args'][5], 'TESTING')
 
    def test_no_for__no_provides_factory_adapts_factory_implements(self):
        from zope.interface import Interface
        from zope.interface import implementer
        from zope.component._declaration import adapter
        from zope.component.zcml import handler
        class IFoo(Interface):
            pass
        @adapter(Interface)
        @implementer(IFoo)
        class _Factory(object):
            def __init__(self, context):
                self.context = context
        _cfg_ctx = self._makeConfigContext()
        self._callFUT(_cfg_ctx, [_Factory])
        self.assertEqual(len(_cfg_ctx._actions), 3)
        self.assertEqual(_cfg_ctx._actions[0][0], ())
        # Register the adapter
        action =_cfg_ctx._actions[0][1]
        self.assertEqual(action['callable'], handler)
        self.assertEqual(action['discriminator'],
                         ('adapter', (Interface,), IFoo, ''))
        self.assertEqual(action['args'],
                         ('registerAdapter', _Factory, (Interface,), IFoo,
                          '', 'TESTING'))


class ResourceViewTests(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        from zope import component
        from zope import security
        from zope.configuration.xmlconfig import XMLConfig
        super(ResourceViewTests, self).setUp()
        XMLConfig('meta.zcml', component)()
        XMLConfig('meta.zcml', security)()

    def _config(self, zcml, testing=0):
        from cStringIO import StringIO
        from zope.configuration.xmlconfig import xmlconfig
        xmlconfig(StringIO(_ZCML_TEMPLATE % zcml), testing=testing)

    def testView(self):
        from zope.component import queryMultiAdapter
        from zope.component.tests.examples import Ob3
        from zope.component.testfiles.views import IV
        from zope.component.testfiles.views import Request
        from zope.component.testfiles.views import V1
        ob = Ob3()
        request = Request(IV)
        self.assertEqual(queryMultiAdapter((ob, request), name=u'test'), None)

        self._config(
            '''
            <view name="test"
                  factory="zope.component.testfiles.views.V1"
                  for="zope.component.testfiles.views.IC"
                  type="zope.component.testfiles.views.IV"/>
            ''')

        view = queryMultiAdapter((ob, request), name=u'test')
        self.assertEqual(view.__class__, V1)

    def testMultiView(self):
        from zope.component import queryMultiAdapter
        from zope.component.tests.examples import Ob3
        from zope.component.testfiles.adapter import A1
        from zope.component.testfiles.adapter import A2
        from zope.component.testfiles.adapter import A3
        from zope.component.testfiles.views import IV
        from zope.component.testfiles.views import Request
        self._config(
            '''
            <view name="test"
                  factory="zope.component.testfiles.adapter.A3"
                  for="zope.component.testfiles.views.IC
                       zope.component.testfiles.adapter.I1
                       zope.component.testfiles.adapter.I2"
                  type="zope.component.testfiles.views.IV"/>
            ''')


        ob = Ob3()
        a1 = A1()
        a2 = A2()
        request = Request(IV)
        view = queryMultiAdapter((ob, a1, a2, request), name=u'test')
        self.assertEqual(view.__class__, A3)
        self.assertEqual(view.context, (ob, a1, a2, request))


    def testMultiView_fails_w_multiple_factories(self):
        from zope.configuration.exceptions import ConfigurationError
        self.assertRaises(ConfigurationError,
            self._config,
            '''
              <view name="test"
                    factory="zope.component.testfiles.adapter.A3
                             zope.component.testfiles.adapter.A2"
                    for="zope.component.testfiles.views.IC
                         zope.component.testfiles.adapter.I1
                         zope.component.testfiles.adapter.I2"
                    type="zope.component.testfiles.views.IV"/>
            ''')

    def testView_w_multiple_factories(self):
        from zope.component import queryMultiAdapter
        from zope.component.tests.examples import Ob3
        from zope.component.testfiles.adapter import A1
        from zope.component.testfiles.adapter import A2
        from zope.component.testfiles.adapter import A3
        from zope.component.testfiles.views import IV
        from zope.component.testfiles.views import Request
        from zope.component.testfiles.views import V1
        self._config(
            '''
            <view name="test"
                  factory="zope.component.testfiles.adapter.A1
                           zope.component.testfiles.adapter.A2
                           zope.component.testfiles.adapter.A3
                           zope.component.testfiles.views.V1"
                  for="zope.component.testfiles.views.IC"
                  type="zope.component.testfiles.views.IV"/>
            ''')

        ob = Ob3()

        # The view should be a V1 around an A3, around an A2, around
        # an A1, anround ob:
        view = queryMultiAdapter((ob, Request(IV)), name=u'test')
        self.assertEqual(view.__class__, V1)
        a3 = view.context
        self.assertEqual(a3.__class__, A3)
        a2 = a3.context[0]
        self.assertEqual(a2.__class__, A2)
        a1 = a2.context[0]
        self.assertEqual(a1.__class__, A1)
        self.assertEqual(a1.context[0], ob)

    def testView_fails_w_no_factories(self):
        from zope.configuration.exceptions import ConfigurationError
        self.assertRaises(ConfigurationError,
            self._config,
            '''
                          <view name="test"
                                   factory=""
                                   for="zope.component.testfiles.views.IC"
                                   type="zope.component.testfiles.views.IV"/>
            ''')


    def testViewThatProvidesAnInterface(self):
        from zope.component import queryMultiAdapter
        from zope.component.tests.examples import Ob3
        from zope.component.testfiles.views import IR
        from zope.component.testfiles.views import IV
        from zope.component.testfiles.views import Request
        from zope.component.testfiles.views import V1
        ob = Ob3()
        self.assertEqual(queryMultiAdapter((ob, Request(IR)), IV, u'test'),
                         None)

        self._config(
            '''
            <view name="test"
                  factory="zope.component.testfiles.views.V1"
                  for="zope.component.testfiles.views.IC"
                  type="zope.component.testfiles.views.IR"
                  />
            ''')

        self.assertEqual(queryMultiAdapter((ob, Request(IR)), IV, u'test'),
                         None)

        self._config(
            '''
            <view name="test"
                  factory="zope.component.testfiles.views.V1"
                  for="zope.component.testfiles.views.IC"
                  type="zope.component.testfiles.views.IR"
                  provides="zope.component.testfiles.views.IV"
                  />
            ''')

        v = queryMultiAdapter((ob, Request(IR)), IV, u'test')
        self.assertEqual(v.__class__, V1)


    def testUnnamedViewThatProvidesAnInterface(self):
        from zope.component import queryMultiAdapter
        from zope.component.tests.examples import Ob3
        from zope.component.testfiles.views import IR
        from zope.component.testfiles.views import IV
        from zope.component.testfiles.views import Request
        from zope.component.testfiles.views import V1
        ob = Ob3()
        self.assertEqual(queryMultiAdapter((ob, Request(IR)), IV), None)

        self._config(
            '''
            <view factory="zope.component.testfiles.views.V1"
                  for="zope.component.testfiles.views.IC"
                  type="zope.component.testfiles.views.IR"
                  />
            ''')

        v = queryMultiAdapter((ob, Request(IR)), IV)
        self.assertEqual(v, None)

        self._config(
            '''
            <view factory="zope.component.testfiles.views.V1"
                  for="zope.component.testfiles.views.IC"
                  type="zope.component.testfiles.views.IR"
                  provides="zope.component.testfiles.views.IV"
                  />
            ''')

        v = queryMultiAdapter((ob, Request(IR)), IV)
        self.assertEqual(v.__class__, V1)

    def testViewHavingARequiredClass(self):
        from zope.interface import implementer
        from zope.component import getMultiAdapter
        from zope.component.interfaces import ComponentLookupError
        from zope.component.testfiles.adapter import A1
        from zope.component.testfiles.components import Content
        from zope.component.testfiles.components import IContent
        from zope.component.testfiles.views import IR
        from zope.component.testfiles.views import Request
        self._config(
            '''
            <view
              for="zope.component.testfiles.components.Content"
              type="zope.component.testfiles.views.IR"
              factory="zope.component.testfiles.adapter.A1"
              />
            ''')

        content = Content()
        a1 = getMultiAdapter((content, Request(IR)))
        self.assert_(isinstance(a1, A1))

        @implementer(IContent)
        class MyContent:
            pass

        self.assertRaises(ComponentLookupError,
                          getMultiAdapter, (MyContent(), Request(IR)))

    def testInterfaceProtectedView(self):
        from zope.security.checker import ProxyFactory
        from zope.component import getMultiAdapter
        from zope.component.tests.examples import Ob3
        from zope.component.testfiles.views import IV
        from zope.component.testfiles.views import Request
        self._config(
            '''
            <view name="test"
                  factory="zope.component.testfiles.views.V1"
                  for="zope.component.testfiles.views.IC"
                  type="zope.component.testfiles.views.IV"
                  permission="zope.Public"
              allowed_interface="zope.component.testfiles.views.IV"
                  />
            ''')

        v = ProxyFactory(getMultiAdapter((Ob3(), Request(IV)), name='test'))
        self.assertEqual(v.index(), 'V1 here')
        self.assertRaises(Exception, getattr, v, 'action')

    def testAttributeProtectedView(self):
        from zope.component import getMultiAdapter
        from zope.component.tests.examples import Ob3
        from zope.component.testfiles.views import IV
        from zope.component.testfiles.views import Request
        from zope.security.checker import ProxyFactory
        self._config(
            '''
            <view name="test"
                  factory="zope.component.testfiles.views.V1"
                  for="zope.component.testfiles.views.IC"
                  type="zope.component.testfiles.views.IV"
                  permission="zope.Public"
                  allowed_attributes="action"
                  />
            ''')

        v = ProxyFactory(getMultiAdapter((Ob3(), Request(IV)), name='test'))
        self.assertEqual(v.action(), 'done')
        self.assertRaises(Exception, getattr, v, 'index')

    def testInterfaceAndAttributeProtectedView(self):
        from zope.component import getMultiAdapter
        from zope.component.tests.examples import Ob3
        from zope.component.testfiles.views import IV
        from zope.component.testfiles.views import Request
        self._config(
            '''
            <view name="test"
                  factory="zope.component.testfiles.views.V1"
                  for="zope.component.testfiles.views.IC"
                  type="zope.component.testfiles.views.IV"
                  permission="zope.Public"
                  allowed_attributes="action"
              allowed_interface="zope.component.testfiles.views.IV"
                  />
            ''')

        v = getMultiAdapter((Ob3(), Request(IV)), name='test')
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')

    def testDuplicatedInterfaceAndAttributeProtectedView(self):
        from zope.component import getMultiAdapter
        from zope.component.tests.examples import Ob3
        from zope.component.testfiles.views import IV
        from zope.component.testfiles.views import Request
        self._config(
            '''
            <view name="test"
                  factory="zope.component.testfiles.views.V1"
                  for="zope.component.testfiles.views.IC"
                  type="zope.component.testfiles.views.IV"
                  permission="zope.Public"
                  allowed_attributes="action index"
              allowed_interface="zope.component.testfiles.views.IV"
                  />
            ''')

        v = getMultiAdapter((Ob3(), Request(IV)), name='test')
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')

    def testIncompleteProtectedViewNoPermission(self):
        from zope.configuration.exceptions import ConfigurationError
        self.assertRaises(
            ConfigurationError,
            self._config,
            '''
            <view name="test"
                  factory="zope.component.testfiles.views.V1"
                  for="zope.component.testfiles.views.IC"
                  type="zope.component.testfiles.views.IV"
                  allowed_attributes="action index"
                  />
            ''',
            )

    def testViewUndefinedPermission(self):
        self.assertRaises(ValueError,
            self._config,
            '''
            <view name="test"
                  factory="zope.component.testfiles.views.V1"
                  for="zope.component.testfiles.views.IC"
                  type="zope.component.testfiles.views.IV"
                  permission="zope.UndefinedPermission"
                  allowed_attributes="action index"
              allowed_interface="zope.component.testfiles.views.IV"
                  />
            ''',
            testing=1)

    def testResource(self):
        from zope.component import queryAdapter
        from zope.component.tests.examples import Ob3
        from zope.component.testfiles.views import IV
        from zope.component.testfiles.views import Request
        from zope.component.testfiles.views import R1
        ob = Ob3()
        self.assertEqual(
            queryAdapter(Request(IV), name=u'test'), None)
        self._config(
            '''
            <resource name="test"
                  factory="zope.component.testfiles.views.R1"
                  type="zope.component.testfiles.views.IV"/>
            ''')

        self.assertEqual(
            queryAdapter(Request(IV), name=u'test').__class__,
            R1)

    def testResourceThatProvidesAnInterface(self):
        from zope.component import queryAdapter
        from zope.component.tests.examples import Ob3
        from zope.component.testfiles.views import IR
        from zope.component.testfiles.views import IV
        from zope.component.testfiles.views import Request
        from zope.component.testfiles.views import R1
        ob = Ob3()
        self.assertEqual(queryAdapter(Request(IR), IV, u'test'),
                         None)

        self._config(
            '''
            <resource
                name="test"
                factory="zope.component.testfiles.views.R1"
                type="zope.component.testfiles.views.IR"
                />
            ''')

        v = queryAdapter(Request(IR), IV, name=u'test')
        self.assertEqual(v, None)

        self._config(
            '''
            <resource
                name="test"
                factory="zope.component.testfiles.views.R1"
                type="zope.component.testfiles.views.IR"
                provides="zope.component.testfiles.views.IV"
                />
            ''')

        v = queryAdapter(Request(IR), IV, name=u'test')
        self.assertEqual(v.__class__, R1)

    def testUnnamedResourceThatProvidesAnInterface(self):
        from zope.component import queryAdapter
        from zope.component.tests.examples import Ob3
        from zope.component.testfiles.views import IR
        from zope.component.testfiles.views import IV
        from zope.component.testfiles.views import Request
        from zope.component.testfiles.views import R1
        ob = Ob3()
        self.assertEqual(queryAdapter(Request(IR), IV), None)

        self._config(
            '''
            <resource
                factory="zope.component.testfiles.views.R1"
                type="zope.component.testfiles.views.IR"
                />
            ''')

        v = queryAdapter(Request(IR), IV)
        self.assertEqual(v, None)

        self._config(
            '''
            <resource
                factory="zope.component.testfiles.views.R1"
                type="zope.component.testfiles.views.IR"
                provides="zope.component.testfiles.views.IV"
                />
            ''')

        v = queryAdapter(Request(IR), IV)
        self.assertEqual(v.__class__, R1)

    def testResourceUndefinedPermission(self):
        self.assertRaises(ValueError,
            self._config,
            '''
            <resource name="test"
                  factory="zope.component.testfiles.views.R1"
                  type="zope.component.testfiles.views.IV"
                  permission="zope.UndefinedPermission"/>
            ''',
            testing=1)


_ZCML_TEMPLATE = """<configure
   xmlns='http://namespaces.zope.org/zope'
   i18n_domain='zope'>
   %s
   </configure>"""


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test_handler),
        unittest.makeSuite(Test__rolledUpFactory),
        unittest.makeSuite(Test_adapter),
        unittest.makeSuite(ResourceViewTests),
    ))
