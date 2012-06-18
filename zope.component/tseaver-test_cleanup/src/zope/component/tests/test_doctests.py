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

from zope import interface, component
from zope.interface.verify import verifyObject
from zope.interface.interfaces import IInterface
from zope.testing import renormalizing
from zope.testrunner.layer import UnitTests

from zope.component.interfaces import ComponentLookupError
from zope.component.interfaces import IComponentArchitecture
from zope.component.interfaces import IComponentLookup
from zope.component.testing import setUp, tearDown, PlacelessSetup
import zope.component.persistentregistry
import zope.component.globalregistry

from zope.configuration.xmlconfig import XMLConfig, xmlconfig
from zope.configuration.exceptions import ConfigurationError
from zope.security.checker import ProxyFactory

from zope.component.testfiles.adapter import A1, A2, A3
from zope.component.testfiles.components import IContent, Content
from zope.component.testfiles.components import IApp
from zope.component.testfiles.views import Request, IC, IV, V1, R1, IR

# side effect gets component-based event dispatcher installed.
# we should obviously make this more explicit
import zope.component.event

class I1(interface.Interface):
    pass
class I2(interface.Interface):
    pass
class I2e(I2):
    pass
class I3(interface.Interface):
    pass

class ITestType(IInterface):
    pass

class U:

    def __init__(self, name):
        self.__name__ = name

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.__name__)

class U1(U):
    interface.implements(I1)

class U12(U):
    interface.implements(I1, I2)

class IA1(interface.Interface):
    pass

class IA2(interface.Interface):
    pass

class IA3(interface.Interface):
    pass

class A:

    def __init__(self, *context):
        self.context = context

    def __repr__(self):
        return "%s%r" % (self.__class__.__name__, self.context)

class A12_1(A):
    component.adapts(I1, I2)
    interface.implements(IA1)

class A12_(A):
    component.adapts(I1, I2)

class A_2(A):
    interface.implements(IA2)

class A_3(A):
    interface.implements(IA3)

class A1_12(U):
    component.adapts(I1)
    interface.implements(IA1, IA2)

class A1_2(U):
    component.adapts(I1)
    interface.implements(IA2)

class A1_23(U):
    component.adapts(I1)
    interface.implements(IA1, IA3)

def noop(*args):
    pass

@component.adapter(I1)
def handle1(x):
    print 'handle1', x

def handle(*objects):
    print 'handle', objects

@component.adapter(I1)
def handle3(x):
    print 'handle3', x

@component.adapter(I1)
def handle4(x):
    print 'handle4', x

class Ob(object):
    interface.implements(I1)
    def __repr__(self):
        return '<instance Ob>'


ob = Ob()

class Ob2(object):
    interface.implements(I2)
    def __repr__(self):
        return '<instance Ob2>'

class Comp(object):
    interface.implements(I2)
    def __init__(self, context):
        self.context = context

comp = Comp(1)

class Comp2(object):
    interface.implements(I3)
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

def testInterfaceCall():
    """Here we test the `adapter_hook()` function that we registered with the
    `zope.interface` adapter hook registry, so that we can call interfaces to
    do adaptation.

    First, we need to register an adapter:

      >>> from zope.component.testing import setUp, tearDown
      >>> setUp()
      >>> component.getGlobalSiteManager().registerAdapter(
      ...     Comp, [I1], I2, '')

    Then we try to adapt `ob` to provide an `I2` interface by calling the `I2`
    interface with the obejct as first argument:

      >>> adapter = I2(ob)
      >>> adapter.__class__ is Comp
      True
      >>> adapter.context is ob
      True

    If no adapter is found, a `TypeError is raised...

      >>> I1(Ob2()) #doctest: +NORMALIZE_WHITESPACE
      Traceback (most recent call last):
      ...
      TypeError: ('Could not adapt', <instance Ob2>,
                  <InterfaceClass zope.component.tests.test_doctests.I1>)

    ...unless we specify an alternative adapter:

      >>> marker = object()
      >>> I2(object(), marker) is marker
      True
      >>> tearDown()
    """

def testNamedAdapter():
    """Make sure that adapters with names are correctly selected from the
    registry.

    First we register some named adapter:

      >>> from zope.component.testing import setUp, tearDown
      >>> setUp()
      >>> component.getGlobalSiteManager().registerAdapter(
      ...     lambda x: 0, [I1], I2, 'foo')

    If an adapter isn't registered for the given object and interface,
    and you provide no default, raise `ComponentLookupError`...

      >>> component.getAdapter(ob, I2, 'bar') \\
      ... #doctest: +NORMALIZE_WHITESPACE
      Traceback (most recent call last):
      ...
      ComponentLookupError:
      (<instance Ob>, <InterfaceClass zope.component.tests.test_doctests.I2>, 'bar')

    ...otherwise, you get the default

      >>> component.queryAdapter(ob, I2, 'bar', '<default>')
      '<default>'

    But now we register an adapter for the object having the correct name

      >>> component.getGlobalSiteManager().registerAdapter(
      ...     Comp, [I1], I2, 'bar')

    so that the lookup succeeds:

      >>> adapter = component.getAdapter(ob, I2, 'bar')
      >>> adapter.__class__ is Comp
      True
      >>> adapter.context is ob
      True
      >>> tearDown()
    """

def testMultiAdapter():
    """Adapting a combination of 2 objects to an interface

    Multi-adapters adapt one or more objects to another interface. To make
    this demonstration non-trivial, we need to create a second object to be
    adapted:

      >>> from zope.component.testing import setUp, tearDown
      >>> setUp()
      >>> ob2 = Ob2()

    Like for regular adapters, if an adapter isn't registered for the given
    objects and interface, and you provide no default, raise
    `ComponentLookupError`...

      >>> component.getMultiAdapter((ob, ob2), I3) \\
      ... #doctest: +NORMALIZE_WHITESPACE
      Traceback (most recent call last):
      ...
      ComponentLookupError:
      ((<instance Ob>, <instance Ob2>),
       <InterfaceClass zope.component.tests.test_doctests.I3>,
       u'')

    ...otherwise, you get the default

      >>> component.queryMultiAdapter((ob, ob2), I3, default='<default>')
      '<default>'

    Note that the name is not a required attribute here.

    To test multi-adapters, we also have to create an adapter class that
    handles to context objects:

      >>> class DoubleAdapter(object):
      ...     interface.implements(I3)
      ...     def __init__(self, first, second):
      ...         self.first = first
      ...         self.second = second

    Now we can register the multi-adapter using

      >>> component.getGlobalSiteManager().registerAdapter(
      ...     DoubleAdapter, (I1, I2), I3, '')

    Notice how the required interfaces are simply provided by a tuple. Now we
    can get the adapter:

      >>> adapter = component.getMultiAdapter((ob, ob2), I3)
      >>> adapter.__class__ is DoubleAdapter
      True
      >>> adapter.first is ob
      True
      >>> adapter.second is ob2
      True
      >>> tearDown()
    """

def testAdapterForInterfaceNone():
    """Providing an adapter for None says that your adapter can adapt anything
    to `I2`.

      >>> from zope.component.testing import setUp, tearDown
      >>> setUp()
      >>> component.getGlobalSiteManager().registerAdapter(
      ...     Comp, (None,), I2, '')

      >>> adapter = I2(ob)
      >>> adapter.__class__ is Comp
      True
      >>> adapter.context is ob
      True

    It can really adapt any arbitrary object:

      >>> something = object()
      >>> adapter = I2(something)
      >>> adapter.__class__ is Comp
      True
      >>> adapter.context is something
      True
      >>> tearDown()
    """

def testGetAdapters():
    """It is sometimes desireable to get a list of all adapters that are
    registered for a particular output interface, given a set of
    objects.

    Let's register some adapters first:

      >>> from zope.component.testing import setUp, tearDown
      >>> setUp()
      >>> component.getGlobalSiteManager().registerAdapter(
      ...     Comp, [I1], I2, '')
      >>> component.getGlobalSiteManager().registerAdapter(
      ...     Comp, [None], I2, 'foo')

    Now we get all the adapters that are registered for `ob` that provide
    `I2`:

      >>> adapters = sorted(component.getAdapters((ob,), I2))
      >>> [(name, adapter.__class__.__name__) for name, adapter in adapters]
      [(u'', 'Comp'), (u'foo', 'Comp')]

    Note that the output doesn't include None values. If an adapter
    factory returns None, it is as if it wasn't present.

      >>> component.getGlobalSiteManager().registerAdapter(
      ...     lambda context: None, [I1], I2, 'nah')
      >>> adapters = sorted(component.getAdapters((ob,), I2))
      >>> [(name, adapter.__class__.__name__) for name, adapter in adapters]
      [(u'', 'Comp'), (u'foo', 'Comp')]
      >>> tearDown()
    """

def testNotBrokenWhenNoSiteManager():
    """Make sure that the adapter lookup is not broken, when no site manager
    is available.

    Both of those things emit `DeprecationWarnings`.

      >>> from zope.component.testing import setUp, tearDown
      >>> setUp()
      >>> I2(ob) #doctest: +NORMALIZE_WHITESPACE
      Traceback (most recent call last):
      ...
      TypeError: ('Could not adapt',
                  <instance Ob>,
                  <InterfaceClass zope.component.tests.test_doctests.I2>)


      >>> I2(ob, 42)
      42
      >>> tearDown()
    """


def testNo__component_adapts__leakage():
    """
    We want to make sure that an `adapts()` call in a class definition
    doesn't affect instances.

      >>> from zope.component.testing import setUp, tearDown
      >>> setUp()
      >>> class C:
      ...     component.adapts()

      >>> C.__component_adapts__
      ()
      >>> C().__component_adapts__
      Traceback (most recent call last):
      ...
      AttributeError: __component_adapts__
      >>> tearDown()
    """

def test_ability_to_pickle_globalsitemanager():
    """
    We need to make sure that it is possible to pickle the global site manager
    and its two global adapter registries.

      >>> from zope.component import globalSiteManager
      >>> from zope.component.testing import setUp, tearDown
      >>> import cPickle
      >>> setUp()
      >>> pickle = cPickle.dumps(globalSiteManager)
      >>> sm = cPickle.loads(pickle)
      >>> sm is globalSiteManager
      True

    Now let's ensure that the registries themselves can be pickled as well:

      >>> pickle = cPickle.dumps(globalSiteManager.adapters)
      >>> adapters = cPickle.loads(pickle)
      >>> adapters is globalSiteManager.adapters
      True
      >>> tearDown()
    """

def test_persistent_component_managers():
    """
Here, we'll demonstrate that changes work even when data are stored in
a database and when accessed from multiple connections.

Start by setting up a database and creating two transaction
managers and database connections to work with.

    >>> from zope.component.testing import setUp, tearDown
    >>> setUp()
    >>> import ZODB.tests.util
    >>> db = ZODB.tests.util.DB()
    >>> import transaction
    >>> t1 = transaction.TransactionManager()
    >>> c1 = db.open(transaction_manager=t1)
    >>> r1 = c1.root()
    >>> t2 = transaction.TransactionManager()
    >>> c2 = db.open(transaction_manager=t2)
    >>> r2 = c2.root()

Create a set of components registries in the database, alternating
connections.

    >>> from zope.component.persistentregistry import PersistentComponents

    >>> _ = t1.begin()
    >>> r1[1] = PersistentComponents('1')
    >>> t1.commit()

    >>> _ = t2.begin()
    >>> r2[2] = PersistentComponents('2', (r2[1], ))
    >>> t2.commit()

    >>> _ = t1.begin()
    >>> r1[3] = PersistentComponents('3', (r1[1], ))
    >>> t1.commit()

    >>> _ = t2.begin()
    >>> r2[4] = PersistentComponents('4', (r2[2], r2[3]))
    >>> t2.commit()

    >>> _ = t1.begin()
    >>> r1[1].__bases__
    ()
    >>> r1[2].__bases__ == (r1[1], )
    True

    >>> r1[1].registerUtility(U1(1))
    >>> r1[1].queryUtility(I1)
    U1(1)
    >>> r1[2].queryUtility(I1)
    U1(1)
    >>> t1.commit()

    >>> _ = t2.begin()
    >>> r2[1].registerUtility(U1(2))
    >>> r2[2].queryUtility(I1)
    U1(2)

    >>> r2[4].queryUtility(I1)
    U1(2)
    >>> t2.commit()


    >>> _ = t1.begin()
    >>> r1[1].registerUtility(U12(1), I2)
    >>> r1[4].queryUtility(I2)
    U12(1)
    >>> t1.commit()


    >>> _ = t2.begin()
    >>> r2[3].registerUtility(U12(3), I2)
    >>> r2[4].queryUtility(I2)
    U12(3)
    >>> t2.commit()

    >>> _ = t1.begin()

    >>> r1[1].registerHandler(handle1, info="First handler")
    >>> r1[2].registerHandler(handle, required=[U])

    >>> r1[3].registerHandler(handle3)

    >>> r1[4].registerHandler(handle4)

    >>> r1[4].handle(U1(1))
    handle1 U1(1)
    handle3 U1(1)
    handle (U1(1),)
    handle4 U1(1)

    >>> t1.commit()

    >>> _ = t2.begin()
    >>> r2[4].handle(U1(1))
    handle1 U1(1)
    handle3 U1(1)
    handle (U1(1),)
    handle4 U1(1)
    >>> t2.abort()

    >>> db.close()
    >>> tearDown()
    """

def persistent_registry_doesnt_scew_up_subsribers():
    """
    >>> from zope.component.testing import setUp, tearDown
    >>> setUp()
    >>> import ZODB.tests.util
    >>> db = ZODB.tests.util.DB()
    >>> import transaction
    >>> t1 = transaction.TransactionManager()
    >>> c1 = db.open(transaction_manager=t1)
    >>> r1 = c1.root()
    >>> t2 = transaction.TransactionManager()
    >>> c2 = db.open(transaction_manager=t2)
    >>> r2 = c2.root()

    >>> from zope.component.persistentregistry import PersistentComponents

    >>> _ = t1.begin()
    >>> r1[1] = PersistentComponents('1')
    >>> r1[1].registerHandler(handle1)
    >>> r1[1].registerSubscriptionAdapter(handle1, provided=I2)
    >>> _ = r1[1].unregisterHandler(handle1)
    >>> _ = r1[1].unregisterSubscriptionAdapter(handle1, provided=I2)
    >>> t1.commit()
    >>> _ = t1.begin()
    >>> r1[1].registerHandler(handle1)
    >>> r1[1].registerSubscriptionAdapter(handle1, provided=I2)
    >>> t1.commit()

    >>> _ = t2.begin()
    >>> len(list(r2[1].registeredHandlers()))
    1
    >>> len(list(r2[1].registeredSubscriptionAdapters()))
    1
    >>> t2.abort()
    >>> tearDown()
    """



class GlobalRegistry:
    pass

base = zope.component.globalregistry.GlobalAdapterRegistry(
    GlobalRegistry, 'adapters')
GlobalRegistry.adapters = base
def clear_base():
    base.__init__(GlobalRegistry, 'adapters')

def test_deghostification_of_persistent_adapter_registries():
    """

We want to make sure that we see updates corrextly.

    >>> import persistent
    >>> import transaction
    >>> class IFoo(interface.Interface):
    ...     pass
    >>> class Foo(persistent.Persistent):
    ...     interface.implements(IFoo)
    ...     name = ''
    ...     def __init__(self, name=''):
    ...         self.name = name
    ...     def __repr__(self):
    ...         return 'Foo(%r)' % self.name

    >>> from zope.component.testing import setUp, tearDown
    >>> setUp()
    >>> len(base._v_subregistries)
    0

    >>> import ZODB.tests.util
    >>> db = ZODB.tests.util.DB()
    >>> tm1 = transaction.TransactionManager()
    >>> c1 = db.open(transaction_manager=tm1)
    >>> r1 = zope.component.persistentregistry.PersistentAdapterRegistry(
    ...           (base,))
    >>> r2 = zope.component.persistentregistry.PersistentAdapterRegistry((r1,))
    >>> c1.root()[1] = r1
    >>> c1.root()[2] = r2
    >>> tm1.commit()
    >>> r1._p_deactivate()

    >>> len(base._v_subregistries)
    0

    >>> tm2 = transaction.TransactionManager()
    >>> c2 = db.open(transaction_manager=tm2)
    >>> r1 = c2.root()[1]
    >>> r2 = c2.root()[2]

    >>> r1.lookup((), IFoo, '')

    >>> base.register((), IFoo, '', Foo(''))
    >>> r1.lookup((), IFoo, '')
    Foo('')

    >>> r2.lookup((), IFoo, '1')

    >>> r1.register((), IFoo, '1', Foo('1'))

    >>> r2.lookup((), IFoo, '1')
    Foo('1')

    >>> r1.lookup((), IFoo, '2')
    >>> r2.lookup((), IFoo, '2')

    >>> base.register((), IFoo, '2', Foo('2'))

    >>> r1.lookup((), IFoo, '2')
    Foo('2')

    >>> r2.lookup((), IFoo, '2')
    Foo('2')

Cleanup:

    >>> db.close()
    >>> clear_base()
    >>> tearDown()
    """


def test_multi_handler_unregistration():
    """
    There was a bug where multiple handlers for the same required
    specification would all be removed when one of them was
    unregistered:

    >>> from zope.component.testing import setUp, tearDown
    >>> setUp()
    >>> class I(zope.interface.Interface):
    ...     pass
    >>> def factory1(event):
    ...     print "| Factory 1 is here"
    >>> def factory2(event):
    ...     print "| Factory 2 is here"
    >>> class Event(object):
    ...     zope.interface.implements(I)
    >>> from zope.interface.registry import Components
    >>> registry = Components()
    >>> registry.registerHandler(factory1, [I,])
    >>> registry.registerHandler(factory2, [I,])
    >>> registry.handle(Event())
    | Factory 1 is here
    | Factory 2 is here
    >>> registry.unregisterHandler(factory1, [I,])
    True
    >>> registry.handle(Event())
    | Factory 2 is here
    >>> tearDown()
    """

def dont_leak_utility_registrations_in__subscribers():
    """

    We've observed utilities getting left in _subscribers when they
    get unregistered.

    >>> from zope.component.testing import setUp, tearDown
    >>> setUp()
    >>> import zope.interface.registry
    >>> reg = zope.interface.registry.Components()
    >>> class C:
    ...     def __init__(self, name):
    ...         self.name = name
    ...     def __repr__(self):
    ...         return "C(%s)" % self.name

    >>> c1 = C(1)
    >>> reg.registerUtility(c1, I1)
    >>> reg.registerUtility(c1, I1)
    >>> list(reg.getAllUtilitiesRegisteredFor(I1))
    [C(1)]

    >>> reg.unregisterUtility(provided=I1)
    True
    >>> list(reg.getAllUtilitiesRegisteredFor(I1))
    []

    >>> reg.registerUtility(c1, I1)
    >>> reg.registerUtility(C(2), I1)

    >>> list(reg.getAllUtilitiesRegisteredFor(I1))
    [C(2)]
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
    interface.implements(IC)

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
            interface.implements(IContent)

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
    tearDown()
    setUp()
    XMLConfig('meta.zcml', component)()

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
