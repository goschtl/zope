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
"""Pure-Python hookable tests
"""
import unittest

from zope.component.testing import PlacelessSetup


class PermissionProxyTests(unittest.TestCase):

    def _getTargetClass(self):
        from zope.component.security import PermissionProxy
        return PermissionProxy

    def _makeOne(self, wrapped):
        return self._getTargetClass()(wrapped)

    def test_proxy_delegates___provided_by__(self):
        from zope.interface import Interface
        from zope.interface import implementer
        from zope.interface import providedBy
        class IFoo(Interface):
            pass
        @implementer(IFoo)
        class Foo(object):
            pass
        foo = Foo()
        proxy = self._makeOne(foo)
        self.assertEqual(providedBy(proxy), providedBy(foo))


class Test__checker(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from zope.component.security import _checker
        return _checker(*args, **kw)

    def test_no_allowed_attributes_no_allowed_interfaces(self):
        from zope.security.checker import CheckerPublic
        checker = self._callFUT(object(), 'zope.Public', (), ())
        self.assertEqual(checker.get_permissions, {'__call__': CheckerPublic})
        self.assertFalse(checker.set_permissions)

    def test_w_allowed_interfaces(self):
        from zope.interface import Interface
        class IFoo(Interface):
            def bar(self):
                pass
            def baz(self):
                pass
        class ISpam(Interface):
            def qux(self):
                pass
        checker = self._callFUT(object(), 'testing', (IFoo, ISpam), ())
        self.assertEqual(checker.get_permissions,
                        {'bar': 'testing', 'baz': 'testing', 'qux': 'testing'})
        self.assertFalse(checker.set_permissions)

    def test_w_allowed_attributes(self):
        checker = self._callFUT(object(), 'testing', (), ('foo', 'bar'))
        self.assertEqual(checker.get_permissions,
                        {'foo': 'testing', 'bar': 'testing'})
        self.assertFalse(checker.set_permissions)


class Test_proxify(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from zope.component.security import proxify
        return proxify(*args, **kw)

    def _makeContext(self):
        class _Context(object):
            def bar(self):
                pass
        return _Context()

    def test_no_checker_no_provides(self):
        ctx = self._makeContext()
        self.assertRaises(ValueError, self._callFUT, ctx, permission='testing')

    def test_no_checker_no_permission(self):
        from zope.interface import Interface
        class IFoo(Interface):
            def bar(self):
                pass
        ctx = self._makeContext()
        self.assertRaises(ValueError, self._callFUT, ctx, provides=IFoo)

    def test_no_checker_w_provides_and_permission_public(self):
        from zope.interface import Interface
        from zope.security.checker import CheckerPublic
        from zope.proxy import getProxiedObject
        class IFoo(Interface):
            def bar(self):
                pass
        ctx = self._makeContext()
        proxy = self._callFUT(ctx, provides=IFoo, permission='zope.Public')
        self.assertTrue(getProxiedObject(proxy) is ctx)
        checker = proxy.__Security_checker__
        self.assertEqual(checker.get_permissions, {'bar': CheckerPublic})
        self.assertFalse(checker.set_permissions)

    def test_no_checker_w_provides_and_permission_protected(self):
        from zope.interface import Interface
        from zope.proxy import getProxiedObject
        class IFoo(Interface):
            def bar(self):
                pass
        ctx = self._makeContext()
        proxy = self._callFUT(ctx, provides=IFoo, permission='testing')
        self.assertTrue(getProxiedObject(proxy) is ctx)
        checker = proxy.__Security_checker__
        self.assertEqual(checker.get_permissions, {'bar': 'testing'})
        self.assertFalse(checker.set_permissions)

    def test_w_checker(self):
        from zope.proxy import getProxiedObject
        _CHECKER = object()
        ctx = self._makeContext()
        proxy = self._callFUT(ctx, _CHECKER)
        self.assertTrue(getProxiedObject(proxy) is ctx)
        self.assertTrue(proxy.__Security_checker__ is _CHECKER)


class Test_protectedFactory(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from zope.component.security import protectedFactory
        return protectedFactory(*args, **kw)

    def test_public_not_already_proxied(self):
        from zope.interface import Interface
        from zope.security.checker import CheckerPublic
        class IFoo(Interface):
            def bar(self):
                pass
        class _Factory(object):
            def bar(self):
                pass
        protected = self._callFUT(_Factory, IFoo, 'zope.Public')
        self.assertTrue(protected.factory is _Factory)
        foo = protected()
        self.assertEqual(foo.__Security_checker__.get_permissions,
                        {'bar': CheckerPublic})

    def test_nonpublic_already_proxied(self):
        from zope.interface import Interface
        from zope.security.proxy import getTestProxyItems
        class IFoo(Interface):
            def bar(self):
                pass
        class _Factory(object):
            __slots__ = ('one',)
            def bar(self):
                pass
        protected = self._callFUT(_Factory, IFoo, 'testing')
        self.assertTrue(protected.factory is _Factory)
        foo = protected()
        self.assertEqual(getTestProxyItems(foo), [('bar', 'testing')])


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
        unittest.makeSuite(PermissionProxyTests),
        unittest.makeSuite(Test__checker),
        unittest.makeSuite(Test_proxify),
        unittest.makeSuite(Test_protectedFactory),
        unittest.makeSuite(ResourceViewTests),
    ))
