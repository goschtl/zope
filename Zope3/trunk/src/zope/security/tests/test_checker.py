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
"""

Revision information:
$Id: test_checker.py,v 1.4 2003/03/07 18:39:44 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.security.checker import Checker, NamesChecker, CheckerPublic
from zope.testing.cleanup import CleanUp
from zope.security.interfaces import ISecurityPolicy
from zope.exceptions import Forbidden, Unauthorized
from zope.security.management import setSecurityPolicy
from zope.security.proxy import getChecker, getObject
from zope.security.checker import defineChecker
import types, pickle

class SecurityPolicy:

    __implements__ =  ISecurityPolicy

    def checkPermission(self, permission, object, context):
        'See ISecurityPolicy'

        return permission == 'test_allowed'


class TransparentProxy(object):
    def __init__(self, ob):
        self._ob = ob

    def __getattribute__(self, name):
        ob = object.__getattribute__(self, '_ob')
        return getattr(ob, name)

class OldInst:
    a=1

    def b(self):
        pass

    c=2

    def gete(self): return 3
    e = property(gete)

    def __getitem__(self, x): return 5, x

    def __setitem__(self, x, v): pass

class NewInst(object, OldInst):

    def gete(self): return 3
    def sete(self, v): pass
    e = property(gete, sete)

class Test(TestCase, CleanUp):

    def setUp(self):
        CleanUp.setUp(self)
        self.__oldpolicy = setSecurityPolicy(SecurityPolicy())

    def tearDown(self):
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
            checker = NamesChecker(['a', 'b', 'c', '__getitem__'],
                                   'perm')

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


        for rock in (1, 1.0, 1l, 1j,
                     '1', u'1', None,
                     AttributeError, AttributeError(),
                     ):
            proxy = checker.proxy(rock)

            self.failUnless(proxy is rock, (rock, type(proxy)))

        for class_ in OldInst, NewInst:
            inst = class_()

            for ob in inst, class_:
                proxy = checker.proxy(ob)
                self.failUnless(getObject(proxy) is ob)
                checker = getChecker(proxy)
                if ob is inst:
                    self.assertEqual(checker.permission_id('__str__'),
                                     None)
                else:
                    self.assertEqual(checker.permission_id('__str__'),
                                     CheckerPublic)

            special = NamesChecker(['a', 'b'], 'test_allowed')
            defineChecker(class_, special)

            for ob in inst, TransparentProxy(inst):
                proxy = checker.proxy(ob)
                self.failUnless(getObject(proxy) is ob)

                checker = getChecker(proxy)
                self.failUnless(checker is special,
                                checker.getPermission_func().__self__)

                proxy2 = checker.proxy(proxy)
                self.failUnless(proxy2 is proxy, [proxy, proxy2])

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

    def testNonPrivateChecker(self):
        from zope.security.checker import NonPrivateChecker
        checker = NonPrivateChecker('p')
        self.assertEqual(checker.permission_id('z'), 'p')
        self.assertEqual(checker.permission_id('_z'), None)

    def testAlwaysAvailable(self):
        from zope.security.checker import NamesChecker
        checker = NamesChecker(())
        class C: pass
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


class TestCheckerPublic(TestCase):

    def test_that_pickling_retains_identity(self):
        self.assert_(pickle.loads(pickle.dumps(CheckerPublic))
                     is
                     CheckerPublic)                                  

def test_suite():
    return TestSuite((
        makeSuite(Test),
        makeSuite(TestCheckerPublic),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
