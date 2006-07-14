##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Security Checker tests

$Id$
"""
from unittest import TestCase, TestSuite, main, makeSuite
from zope.interface import implements
from zope.interface.verify import verifyObject
from zope.security.checker import Checker, NamesChecker, CheckerPublic
from zope.testing.cleanup import CleanUp
from zope.security.interfaces import ISecurityPolicy
from zope.security.interfaces import Forbidden, ForbiddenAttribute
from zope.security.interfaces import Unauthorized
from zope.security.management import setSecurityPolicy, newInteraction
from zope.security.management import endInteraction, getInteraction
from zope.security.proxy import removeSecurityProxy
from zope.security.proxy import getChecker
from zope.security.checker import defineChecker, ProxyFactory
from zope.security.proxy import Proxy
import types, pickle

class SecurityPolicy(object):
    implements(ISecurityPolicy)

    def checkPermission(self, permission, object):
        'See ISecurityPolicy'
        return permission == 'test_allowed'

class RecordedSecurityPolicy(object):
    implements(ISecurityPolicy)

    def __init__(self):
        self._checked = []
        self.permissions = {}

    def checkPermission(self, permission, object):
        'See ISecurityPolicy'
        self._checked.append(permission)
        return self.permissions.get(permission, True)

    def checkChecked(self, checked):
        res = self._checked == checked
        self._checked = []
        return res

class TransparentProxy(object):
    def __init__(self, ob):
        self._ob = ob

    def __getattribute__(self, name):
        ob = object.__getattribute__(self, '_ob')
        return getattr(ob, name)

class OldInst:
    __metaclass__ = types.ClassType

    a = 1

    def b(self):
        pass

    c = 2

    def gete(self):
        return 3
    e = property(gete)

    def __getitem__(self, x):
        return 5, x

    def __setitem__(self, x, v):
        pass

class NewInst(object, OldInst):
    # This is not needed, but left in to show the change of metaclass
    # __metaclass__ = type

    def gete(self):
        return 3

    def sete(self, v):
        pass

    e = property(gete, sete)


class Test(TestCase, CleanUp):

    def setUp(self):
        CleanUp.setUp(self)
        self.__oldpolicy = setSecurityPolicy(SecurityPolicy)
        newInteraction()

    def tearDown(self):
        endInteraction()
        setSecurityPolicy(self.__oldpolicy)
        CleanUp.tearDown(self)

    def test_typesAcceptedByDefineChecker(self):
        class ClassicClass:
            __metaclass__ = types.ClassType
        class NewStyleClass:
            __metaclass__ = type
        import zope.security
        not_a_type = object()
        defineChecker(ClassicClass, NamesChecker())
        defineChecker(NewStyleClass, NamesChecker())
        defineChecker(zope.security, NamesChecker())
        self.assertRaises(TypeError,
                defineChecker, not_a_type, NamesChecker())

    # check_getattr cases:
    #
    # - no attribute there
    # - method
    # - allow and disallow by permission
    def test_check_getattr(self):

        oldinst = OldInst()
        oldinst.d = OldInst()

        newinst = NewInst()
        newinst.d = NewInst()

        for inst in oldinst, newinst:
            checker = NamesChecker(['a', 'b', 'c', '__getitem__'], 'perm')

            self.assertRaises(Unauthorized, checker.check_getattr, inst, 'a')
            self.assertRaises(Unauthorized, checker.check_getattr, inst, 'b')
            self.assertRaises(Unauthorized, checker.check_getattr, inst, 'c')
            self.assertRaises(Unauthorized, checker.check, inst, '__getitem__')
            self.assertRaises(Forbidden, checker.check, inst, '__setitem__')
            self.assertRaises(Forbidden, checker.check_getattr, inst, 'd')
            self.assertRaises(Forbidden, checker.check_getattr, inst, 'e')
            self.assertRaises(Forbidden, checker.check_getattr, inst, 'f')

            checker = NamesChecker(['a', 'b', 'c', '__getitem__'],
                                   'test_allowed')

            checker.check_getattr(inst, 'a')
            checker.check_getattr(inst, 'b')
            checker.check_getattr(inst, 'c')
            checker.check(inst, '__getitem__')
            self.assertRaises(Forbidden, checker.check, inst, '__setitem__')
            self.assertRaises(Forbidden, checker.check_getattr, inst, 'd')
            self.assertRaises(Forbidden, checker.check_getattr, inst, 'e')
            self.assertRaises(Forbidden, checker.check_getattr, inst, 'f')

            checker = NamesChecker(['a', 'b', 'c', '__getitem__'],
                                   CheckerPublic)

            checker.check_getattr(inst, 'a')
            checker.check_getattr(inst, 'b')
            checker.check_getattr(inst, 'c')
            checker.check(inst, '__getitem__')
            self.assertRaises(Forbidden, checker.check, inst, '__setitem__')
            self.assertRaises(Forbidden, checker.check_getattr, inst, 'd')
            self.assertRaises(Forbidden, checker.check_getattr, inst, 'e')
            self.assertRaises(Forbidden, checker.check_getattr, inst, 'f')

    def test_check_setattr(self):

        oldinst = OldInst()
        oldinst.d = OldInst()

        newinst = NewInst()
        newinst.d = NewInst()

        for inst in oldinst, newinst:
            checker = Checker({}, {'a': 'perm', 'z': 'perm'})

            self.assertRaises(Unauthorized, checker.check_setattr, inst, 'a')
            self.assertRaises(Unauthorized, checker.check_setattr, inst, 'z')
            self.assertRaises(Forbidden, checker.check_setattr, inst, 'c')
            self.assertRaises(Forbidden, checker.check_setattr, inst, 'd')
            self.assertRaises(Forbidden, checker.check_setattr, inst, 'e')
            self.assertRaises(Forbidden, checker.check_setattr, inst, 'f')

            checker = Checker({}, {'a': 'test_allowed', 'z': 'test_allowed'})

            checker.check_setattr(inst, 'a')
            checker.check_setattr(inst, 'z')
            self.assertRaises(Forbidden, checker.check_setattr, inst, 'd')
            self.assertRaises(Forbidden, checker.check_setattr, inst, 'e')
            self.assertRaises(Forbidden, checker.check_setattr, inst, 'f')

            checker = Checker({}, {'a': CheckerPublic, 'z': CheckerPublic})

            checker.check_setattr(inst, 'a')
            checker.check_setattr(inst, 'z')
            self.assertRaises(Forbidden, checker.check_setattr, inst, 'd')
            self.assertRaises(Forbidden, checker.check_setattr, inst, 'e')
            self.assertRaises(Forbidden, checker.check_setattr, inst, 'f')

    def test_proxy(self):
        checker = NamesChecker(())

        from zope.security.checker import BasicTypes_examples
        rocks = tuple(BasicTypes_examples.values())
        for rock in rocks:
            proxy = checker.proxy(rock)
            self.failUnless(proxy is rock, (rock, type(proxy)))

        for class_ in OldInst, NewInst:
            inst = class_()

            for ob in inst, class_:
                proxy = checker.proxy(ob)
                self.failUnless(removeSecurityProxy(proxy) is ob)
                checker = getChecker(proxy)
                if ob is inst:
                    self.assertEqual(checker.permission_id('__str__'),
                                     None)
                else:
                    self.assertEqual(checker.permission_id('__str__'),
                                     CheckerPublic)

            #No longer doing anything special for transparent proxies.
            #A proxy needs to provide its own security checker.
            #
            #special = NamesChecker(['a', 'b'], 'test_allowed')
            #defineChecker(class_, special)
            #
            #for ob in inst, TransparentProxy(inst):
            #    proxy = checker.proxy(ob)
            #    self.failUnless(removeSecurityProxy(proxy) is ob)
            #
            #    checker = getChecker(proxy)
            #    self.failUnless(checker is special,
            #                    checker.get_permissions)
            #
            #    proxy2 = checker.proxy(proxy)
            #    self.failUnless(proxy2 is proxy, [proxy, proxy2])

    def testMultiChecker(self):
        from zope.interface import Interface

        class I1(Interface):
            def f1(): ''
            def f2(): ''

        class I2(I1):
            def f3(): ''
            def f4(): ''

        class I3(Interface):
            def g(): ''

        from zope.exceptions import DuplicationError

        from zope.security.checker import MultiChecker

        self.assertRaises(DuplicationError,
                          MultiChecker,
                          [(I1, 'p1'), (I2, 'p2')])

        self.assertRaises(DuplicationError,
                          MultiChecker,
                          [(I1, 'p1'), {'f2': 'p2'}])

        MultiChecker([(I1, 'p1'), (I2, 'p1')])

        checker = MultiChecker([
            (I2, 'p1'),
            {'a': 'p3'},
            (I3, 'p2'),
            (('x','y','z'), 'p4'),
            ])

        self.assertEqual(checker.permission_id('f1'), 'p1')
        self.assertEqual(checker.permission_id('f2'), 'p1')
        self.assertEqual(checker.permission_id('f3'), 'p1')
        self.assertEqual(checker.permission_id('f4'), 'p1')
        self.assertEqual(checker.permission_id('g'), 'p2')
        self.assertEqual(checker.permission_id('a'), 'p3')
        self.assertEqual(checker.permission_id('x'), 'p4')
        self.assertEqual(checker.permission_id('y'), 'p4')
        self.assertEqual(checker.permission_id('z'), 'p4')
        self.assertEqual(checker.permission_id('zzz'), None)

    def testAlwaysAvailable(self):
        from zope.security.checker import NamesChecker
        checker = NamesChecker(())
        class C(object): pass
        self.assertEqual(checker.check(C, '__hash__'), None)
        self.assertEqual(checker.check(C, '__nonzero__'), None)
        self.assertEqual(checker.check(C, '__class__'), None)
        self.assertEqual(checker.check(C, '__implements__'), None)
        self.assertEqual(checker.check(C, '__lt__'), None)
        self.assertEqual(checker.check(C, '__le__'), None)
        self.assertEqual(checker.check(C, '__gt__'), None)
        self.assertEqual(checker.check(C, '__ge__'), None)
        self.assertEqual(checker.check(C, '__eq__'), None)
        self.assertEqual(checker.check(C, '__ne__'), None)

    def test_setattr(self):
        checker = NamesChecker(['a', 'b', 'c', '__getitem__'],
                               'test_allowed')

        for inst in NewInst(), OldInst():
            self.assertRaises(Forbidden, checker.check_setattr, inst, 'a')
            self.assertRaises(Forbidden, checker.check_setattr, inst, 'z')

    # TODO: write a test to see that
    # Checker.check/check_setattr handle permission
    # values that evaluate to False

    def test_ProxyFactory(self):
        class SomeClass(object):
            pass
        import zope.security
        checker = NamesChecker()
        specific_checker = NamesChecker()
        checker_as_magic_attr = NamesChecker()

        obj = SomeClass()

        proxy = ProxyFactory(obj)
        self.assert_(type(proxy) is Proxy)
        from zope.security.checker import _defaultChecker
        self.assert_(getChecker(proxy) is _defaultChecker)

        defineChecker(SomeClass, checker)

        proxy = ProxyFactory(obj)
        self.assert_(type(proxy) is Proxy)
        self.assert_(getChecker(proxy) is checker)

        obj.__Security_checker__ = checker_as_magic_attr

        proxy = ProxyFactory(obj)
        self.assert_(type(proxy) is Proxy)
        self.assert_(getChecker(proxy) is checker_as_magic_attr)

        proxy = ProxyFactory(obj, specific_checker)
        self.assert_(type(proxy) is Proxy)
        self.assert_(getChecker(proxy) is specific_checker)

    def test_ProxyFactory_using_proxy(self):
        class SomeClass(object):
            pass
        obj = SomeClass()
        checker = NamesChecker()
        proxy1 = ProxyFactory(obj)

        proxy2 = ProxyFactory(proxy1)
        self.assert_(proxy1 is proxy2)

        # Trying to change the checker on a proxy.
        self.assertRaises(TypeError, ProxyFactory, proxy1, checker)

        # Setting exactly the same checker as the proxy already has.
        proxy1 = ProxyFactory(obj, checker)
        proxy2 = ProxyFactory(proxy1, checker)
        self.assert_(proxy1 is proxy2)


class TestCheckerPublic(TestCase):

    def test_that_pickling_CheckerPublic_retains_identity(self):
        self.assert_(pickle.loads(pickle.dumps(CheckerPublic))
                     is
                     CheckerPublic)

    def test_that_CheckerPublic_identity_works_even_when_proxied(self):
        self.assert_(ProxyFactory(CheckerPublic) is CheckerPublic)


class TestMixinDecoratedChecker(TestCase):

    def decoratedSetUp(self):
        self.policy = RecordedSecurityPolicy
        self._oldpolicy = setSecurityPolicy(self.policy)
        newInteraction()
        self.interaction = getInteraction()
        self.obj = object()

    def decoratedTearDown(self):
        endInteraction()
        setSecurityPolicy(self._oldpolicy)

    def check_checking_impl(self, checker):
        o = self.obj
        checker.check_getattr(o, 'both_get_set')
        self.assert_(self.interaction.checkChecked(['dc_get_permission']))
        checker.check_getattr(o, 'c_only')
        self.assert_(self.interaction.checkChecked(['get_permission']))
        checker.check_getattr(o, 'd_only')
        self.assert_(self.interaction.checkChecked(['dc_get_permission']))
        self.assertRaises(ForbiddenAttribute,
                          checker.check_getattr, o,
                          'completely_different_attr')
        self.assert_(self.interaction.checkChecked([]))
        checker.check(o, '__str__')
        self.assert_(self.interaction.checkChecked(['get_permission']))

        checker.check_setattr(o, 'both_get_set')
        self.assert_(self.interaction.checkChecked(['dc_set_permission']))
        self.assertRaises(ForbiddenAttribute,
                          checker.check_setattr, o, 'c_only')
        self.assert_(self.interaction.checkChecked([]))
        self.assertRaises(ForbiddenAttribute,
                          checker.check_setattr, o, 'd_only')
        self.assert_(self.interaction.checkChecked([]))

    originalChecker = NamesChecker(['both_get_set', 'c_only', '__str__'],
                                   'get_permission')

    decorationSetMap = {'both_get_set': 'dc_set_permission'}

    decorationGetMap = {'both_get_set': 'dc_get_permission',
                        'd_only': 'dc_get_permission'}

    overridingChecker = Checker(decorationGetMap, decorationSetMap)

class TestCombinedChecker(TestMixinDecoratedChecker, TestCase):

    def setUp(self):
        TestCase.setUp(self)
        self.decoratedSetUp()

    def tearDown(self):
        self.decoratedTearDown()
        TestCase.tearDown(self)

    def test_checking(self):
        from zope.security.checker import CombinedChecker
        cc = CombinedChecker(self.overridingChecker, self.originalChecker)
        self.check_checking_impl(cc)

        # When a permission is not authorized by the security policy,
        # the policy is queried twice per check_getattr -- once for each
        # checker.
        self.interaction.permissions['dc_get_permission'] = False
        cc.check_getattr(self.obj, 'both_get_set')
        self.assert_(
            self.interaction.checkChecked(['dc_get_permission', 'get_permission'])
            )

        # This should raise Unauthorized instead of ForbiddenAttribute, since
        # access can be granted if you e.g. login with different credentials.
        self.assertRaises(Unauthorized, cc.check_getattr, self.obj, 'd_only')
        self.assertRaises(Unauthorized, cc.check, self.obj, 'd_only')

    def test_interface(self):
        from zope.security.checker import CombinedChecker
        from zope.security.interfaces import IChecker
        dc = CombinedChecker(self.overridingChecker, self.originalChecker)
        verifyObject(IChecker, dc)

def test_suite():
    return TestSuite((
        makeSuite(Test),
        makeSuite(TestCheckerPublic),
        makeSuite(TestCombinedChecker),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
