##############################################################################
#
# Copyright (c) 2001, 2002, 2009 Zope Foundation and Contributors.
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
"""Component Architecture Tests
"""
import unittest

from zope.configuration.xmlconfig import XMLConfig, xmlconfig
from zope.configuration.exceptions import ConfigurationError
from zope.interface import Interface
from zope.interface import implements
from zope.interface.interfaces import IInterface
from zope.security.checker import ProxyFactory
from zope.testrunner.layer import UnitTests

from zope.component.interfaces import ComponentLookupError
from zope.component.interfaces import IComponentLookup
from zope.component.testfiles.adapter import A1
from zope.component.testfiles.adapter import A2
from zope.component.testfiles.adapter import A3
from zope.component.testfiles.components import Content
from zope.component.testfiles.components import IContent
from zope.component.testfiles.views import Request
from zope.component.testfiles.views import IC
from zope.component.testfiles.views import IV
from zope.component.testfiles.views import V1
from zope.component.testfiles.views import R1
from zope.component.testfiles.views import IR
from zope.component.testing import setUp
from zope.component.testing import tearDown
from zope.component.testing import PlacelessSetup

# side effect gets component-based event dispatcher installed.
# we should obviously make this more explicit
import zope.component.event

class I1(Interface):
    pass
class I2(Interface):
    pass
class I3(Interface):
    pass

class ITestType(IInterface):
    pass

def noop(*args):
    pass

class Ob(object):
    implements(I1)
    def __repr__(self):
        return '<instance Ob>'


ob = Ob()

class Ob2(object):
    implements(I2)
    def __repr__(self):
        return '<instance Ob2>'

class Comp(object):
    implements(I2)
    def __init__(self, context):
        self.context = context

comp = Comp(1)

class Comp2(object):
    implements(I3)
    def __init__(self, context):
        self.context = context


class ConformsToIComponentLookup(object):
    """This object allows the sitemanager to conform/adapt to
    `IComponentLookup` and thus to itself."""

    def __init__(self, sitemanager):
        self.sitemanager = sitemanager

    def __conform__(self, interface):
        """This method is specified by the adapter PEP to do the adaptation."""
        if interface is IComponentLookup:
            return self.sitemanager


def testNo__component_adapts__leakage():
    """
    We want to make sure that an `adapts()` call in a class definition
    doesn't affect instances.

      >>> from zope.component.testing import setUp, tearDown
      >>> from zope.component import adapts
      >>> setUp()
      >>> class C:
      ...     adapts()

      >>> C.__component_adapts__
      ()
      >>> C().__component_adapts__
      Traceback (most recent call last):
      ...
      AttributeError: __component_adapts__
      >>> tearDown()
    """

def test_zcml_handler_site_manager():
    """
    The ZCML directives provided by zope.component use the ``getSiteManager``
    method to get the registry where to register the components. This makes
    possible to hook ``getSiteManager`` before loading a ZCML file:

    >>> from zope.component.testing import setUp, tearDown
    >>> setUp()
    >>> from zope.interface.registry import Components
    >>> registry = Components()
    >>> def dummy(context=None):
    ...     return registry
    >>> from zope.component import getSiteManager
    >>> ignore = getSiteManager.sethook(dummy)

    >>> from zope.component.testfiles.components import comp, IApp
    >>> from zope.component.zcml import handler
    >>> handler('registerUtility', comp, IApp, u'')
    >>> registry.getUtility(IApp) is comp
    True
    >>> ignore = getSiteManager.reset()
    >>> tearDown()
    """

class StandaloneTests(unittest.TestCase):
    def testStandalone(self):
        import subprocess
        import sys
        import os
        import tempfile
        import pickle

        executable = os.path.abspath(sys.executable)
        program = os.path.join(os.path.dirname(__file__), 'standalonetests.py')
        process = subprocess.Popen([executable, program],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   stdin=subprocess.PIPE)
        pickle.dump(sys.path, process.stdin)
        process.stdin.close()

        try:
            process.wait()
        except OSError, e:
            if e.errno != 4: # MacIntel raises apparently unimportant EINTR?
                raise # TODO verify sanity of a pass on EINTR :-/
        lines = process.stdout.readlines()
        process.stdout.close()
        success = True
        # Interpret the result: We scan the output from the end backwards
        # until we find either a line that says 'OK' (which means the tests
        # ran successfully) or a line that starts with quite a few dashes
        # (which means we didn't find a line that says 'OK' within the summary
        # of the test runner and the tests did not run successfully.)
        for l in reversed(lines):
            l = l.strip()
            if not l:
                continue
            if l.startswith('-----'):
                break
            if l.endswith('OK'):
                sucess = True
        if not success:
            self.fail(''.join(lines))

class HookableTests(unittest.TestCase):

    def test_ctor_no_func(self):
        from zope.component.hookable import hookable
        self.assertRaises(TypeError, hookable)

    def test_ctor_simple(self):
        from zope.component.hookable import hookable
        def foo():
            pass
        hooked = hookable(foo)
        self.failUnless(hooked.original is foo)
        self.failUnless(hooked.implementation is foo)

    def test_ctor_extra_arg(self):
        from zope.component.hookable import hookable
        def foo():
            pass
        self.assertRaises(TypeError, hookable, foo, foo)

    def test_ctor_extra_arg(self):
        from zope.component.hookable import hookable
        def foo():
            pass
        self.assertRaises(TypeError, hookable, foo, nonesuch=foo)

    def test_sethook(self):
        from zope.component.hookable import hookable
        def foo():
            pass
        def bar():
            pass
        hooked = hookable(foo)
        hooked.sethook(bar)
        self.failUnless(hooked.original is foo)
        self.failUnless(hooked.implementation is bar)

    def test_reset(self):
        from zope.component.hookable import hookable
        def foo():
            pass
        def bar():
            pass
        hooked = hookable(foo)
        hooked.sethook(bar)
        hooked.reset()
        self.failUnless(hooked.original is foo)
        self.failUnless(hooked.implementation is foo)

    def test_cant_assign_original(self):
        from zope.component.hookable import hookable
        def foo():
            pass
        def bar():
            pass
        hooked = hookable(foo)
        try:
            hooked.original = bar
        except TypeError:
            pass
        except AttributeError:
            pass
        else:
            self.fail('Assigned original')

    def test_cant_delete_original(self):
        from zope.component.hookable import hookable
        def foo():
            pass
        hooked = hookable(foo)
        try:
            del hooked.original
        except TypeError:
            pass
        except AttributeError:
            pass
        else:
            self.fail('Deleted original')

    def test_cant_assign_original(self):
        from zope.component.hookable import hookable
        def foo():
            pass
        def bar():
            pass
        hooked = hookable(foo)
        try:
            hooked.implementation = bar
        except TypeError:
            pass
        except AttributeError:
            pass
        else:
            self.fail('Assigned implementation')

    def test_readonly_original(self):
        from zope.component.hookable import hookable
        def foo():
            pass
        hooked = hookable(foo)
        try:
            del hooked.implementation
        except TypeError:
            pass
        except AttributeError:
            pass
        else:
            self.fail('Deleted implementation')

class Ob3(object):
    implements(IC)

template = """<configure
   xmlns='http://namespaces.zope.org/zope'
   i18n_domain='zope'>
   %s
   </configure>"""


class ResourceViewTests(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(ResourceViewTests, self).setUp()
        XMLConfig('meta.zcml', zope.component)()
        XMLConfig('meta.zcml', zope.security)()

    def _config(self, zcml, testing=0):
        from cStringIO import StringIO
        xmlconfig(StringIO(template % zcml), testing=testing)

    def testView(self):
        ob = Ob3()
        request = Request(IV)
        self.assertEqual(
            zope.component.queryMultiAdapter((ob, request), name=u'test'), None)

        self._config(
            '''
            <view name="test"
                  factory="zope.component.testfiles.views.V1"
                  for="zope.component.testfiles.views.IC"
                  type="zope.component.testfiles.views.IV"/>
            ''')

        self.assertEqual(
            zope.component.queryMultiAdapter((ob, request),
                                             name=u'test').__class__,
            V1)


    def testMultiView(self):
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
        view = zope.component.queryMultiAdapter((ob, a1, a2, request),
                                                name=u'test')
        self.assertEqual(view.__class__, A3)
        self.assertEqual(view.context, (ob, a1, a2, request))


    def testMultiView_fails_w_multiple_factories(self):
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
        view = zope.component.queryMultiAdapter((ob, Request(IV)), name=u'test')
        self.assertEqual(view.__class__, V1)
        a3 = view.context
        self.assertEqual(a3.__class__, A3)
        a2 = a3.context[0]
        self.assertEqual(a2.__class__, A2)
        a1 = a2.context[0]
        self.assertEqual(a1.__class__, A1)
        self.assertEqual(a1.context[0], ob)

    def testView_fails_w_no_factories(self):
        self.assertRaises(ConfigurationError,
            self._config,
            '''
                          <view name="test"
                                   factory=""
                                   for="zope.component.testfiles.views.IC"
                                   type="zope.component.testfiles.views.IV"/>
            ''')


    def testViewThatProvidesAnInterface(self):
        ob = Ob3()
        self.assertEqual(
            zope.component.queryMultiAdapter((ob, Request(IR)), IV, u'test'),
            None)

        self._config(
            '''
            <view name="test"
                  factory="zope.component.testfiles.views.V1"
                  for="zope.component.testfiles.views.IC"
                  type="zope.component.testfiles.views.IR"
                  />
            ''')

        self.assertEqual(
            zope.component.queryMultiAdapter((ob, Request(IR)), IV, u'test'),
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

        v = zope.component.queryMultiAdapter((ob, Request(IR)), IV, u'test')
        self.assertEqual(v.__class__, V1)


    def testUnnamedViewThatProvidesAnInterface(self):
        ob = Ob3()
        self.assertEqual(
            zope.component.queryMultiAdapter((ob, Request(IR)), IV), None)

        self._config(
            '''
            <view factory="zope.component.testfiles.views.V1"
                  for="zope.component.testfiles.views.IC"
                  type="zope.component.testfiles.views.IR"
                  />
            ''')

        v = zope.component.queryMultiAdapter((ob, Request(IR)), IV)
        self.assertEqual(v, None)

        self._config(
            '''
            <view factory="zope.component.testfiles.views.V1"
                  for="zope.component.testfiles.views.IC"
                  type="zope.component.testfiles.views.IR"
                  provides="zope.component.testfiles.views.IV"
                  />
            ''')

        v = zope.component.queryMultiAdapter((ob, Request(IR)), IV)
        self.assertEqual(v.__class__, V1)

    def testViewHavingARequiredClass(self):
        self._config(
            '''
            <view
              for="zope.component.testfiles.components.Content"
              type="zope.component.testfiles.views.IR"
              factory="zope.component.testfiles.adapter.A1"
              />
            ''')

        content = Content()
        a1 = zope.component.getMultiAdapter((content, Request(IR)))
        self.assert_(isinstance(a1, A1))

        class MyContent:
            implements(IContent)

        self.assertRaises(ComponentLookupError, zope.component.getMultiAdapter,
                          (MyContent(), Request(IR)))

    def testInterfaceProtectedView(self):
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

        v = ProxyFactory(zope.component.getMultiAdapter((Ob3(), Request(IV)),
                                                        name='test'))
        self.assertEqual(v.index(), 'V1 here')
        self.assertRaises(Exception, getattr, v, 'action')

    def testAttributeProtectedView(self):
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

        v = ProxyFactory(zope.component.getMultiAdapter((Ob3(), Request(IV)),
                                                        name='test'))
        self.assertEqual(v.action(), 'done')
        self.assertRaises(Exception, getattr, v, 'index')

    def testInterfaceAndAttributeProtectedView(self):
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

        v = zope.component.getMultiAdapter((Ob3(), Request(IV)), name='test')
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')

    def testDuplicatedInterfaceAndAttributeProtectedView(self):
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

        v = zope.component.getMultiAdapter((Ob3(), Request(IV)), name='test')
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')

    def testIncompleteProtectedViewNoPermission(self):
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
        ob = Ob3()
        self.assertEqual(
            zope.component.queryAdapter(Request(IV), name=u'test'), None)
        self._config(
            '''
            <resource name="test"
                  factory="zope.component.testfiles.views.R1"
                  type="zope.component.testfiles.views.IV"/>
            ''')

        self.assertEqual(
            zope.component.queryAdapter(Request(IV), name=u'test').__class__,
            R1)

    def testResourceThatProvidesAnInterface(self):
        ob = Ob3()
        self.assertEqual(zope.component.queryAdapter(Request(IR), IV, u'test'),
                         None)

        self._config(
            '''
            <resource
                name="test"
                factory="zope.component.testfiles.views.R1"
                type="zope.component.testfiles.views.IR"
                />
            ''')

        v = zope.component.queryAdapter(Request(IR), IV, name=u'test')
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

        v = zope.component.queryAdapter(Request(IR), IV, name=u'test')
        self.assertEqual(v.__class__, R1)

    def testUnnamedResourceThatProvidesAnInterface(self):
        ob = Ob3()
        self.assertEqual(zope.component.queryAdapter(Request(IR), IV), None)

        self._config(
            '''
            <resource
                factory="zope.component.testfiles.views.R1"
                type="zope.component.testfiles.views.IR"
                />
            ''')

        v = zope.component.queryAdapter(Request(IR), IV)
        self.assertEqual(v, None)

        self._config(
            '''
            <resource
                factory="zope.component.testfiles.views.R1"
                type="zope.component.testfiles.views.IR"
                provides="zope.component.testfiles.views.IV"
                />
            ''')

        v = zope.component.queryAdapter(Request(IR), IV)
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


class ConditionalSecurityLayer(UnitTests):

    __name__ = 'ConditionalSecurity'
    __bases__ = ()

    def setUp(self):
        import sys
        import zope.component.zcml
        setUp()
        self.modules = {}
        for m in ('zope.security', 'zope.proxy'):
            self.modules[m] = sys.modules[m]
            sys.modules[m] = None
        reload(zope.component.zcml)

    def tearDown(self):
        import sys
        import zope.component.zcml
        tearDown()
        for m in ('zope.security', 'zope.proxy'):
            sys.modules[m] = self.modules[m]
        reload(zope.component.zcml)


def setUpRegistryTests(tests):
    setUp()

def tearDownRegistryTests(tests):
    tearDown()
    import zope.event
    zope.event.subscribers.pop()

def clearZCML(test=None):
    import zope.component
    tearDown()
    setUp()
    XMLConfig('meta.zcml', zope.component)()

def test_suite():
    import doctest
    return unittest.TestSuite((
        doctest.DocTestSuite(setUp=setUp, tearDown=tearDown),
        unittest.makeSuite(HookableTests),
        doctest.DocTestSuite('zope.component.interface',
                             setUp=setUp, tearDown=tearDown),
        doctest.DocTestSuite('zope.component.nexttesting'),
        unittest.makeSuite(StandaloneTests),
        unittest.makeSuite(ResourceViewTests),
        ))
