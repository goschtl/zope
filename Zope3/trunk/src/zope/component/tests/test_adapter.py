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

import unittest

from zope.component.adapter import GlobalAdapterService
from zope.interface import Interface

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

class GlobalAdapterServiceTests(unittest.TestCase):
    
    def getRegistry(self):
        registry = GlobalAdapterService()

        registry.register([None], P3, '', default_P3)
        registry.register([Interface], P3, '', any_P3)
        registry.register([R2], P3, '', R2_P3)

        return registry
    
    def test_getRegisteredMatching_all(self):
        registry = self.getRegistry()

        got = list(registry.getRegisteredMatching())
        got.sort()
        expect = [
            (Interface, P3, (), u'', any_P3),
            (R2, P3, (), u'', R2_P3),
            (None, P3, (), u'', default_P3),
            ]
        expect.sort()
        self.assertEqual(got, expect)

    def test_getRegisteredMatching_for_R1(self):
        registry = self.getRegistry()

        got = list(registry.getRegisteredMatching(
            required = (R1, )
            ))
        got.sort()
        expect = [
            (Interface, P3, (), u'', any_P3),
            (None, P3, (), u'', default_P3),
            ]
        expect.sort()
        self.assertEqual(got, expect)

    def test_getRegisteredMatching_for_multiple(self):
        registry = self.getRegistry()

        got = list(registry.getRegisteredMatching(
            required = (R12, R2)
            ))
        got.sort()
        expect = [
            (Interface, P3, (), u'', any_P3),
            (R2, P3, (), u'', R2_P3),
            (None, P3, (), u'', default_P3),
            ]
        expect.sort()
        self.assertEqual(got, expect)

    def test_getRegisteredMatching_provided_P1(self):
        registry = self.getRegistry()

        got = list(registry.getRegisteredMatching(
            provided = (P1, )
            ))

        got.sort()
        expect = [
            (Interface, P3, (), u'', any_P3),
            (R2, P3, (), u'', R2_P3),
            (None, P3, (), u'', default_P3),
            ]
        expect.sort()
        self.assertEqual(got, expect)

    def test_getRegisteredMatching_provided_P2(self):
        registry = self.getRegistry()

        got = list(registry.getRegisteredMatching(
            provided = (P3, )
            ))
        got.sort()
        expect = [
            (Interface, P3, (), u'', any_P3),
            (R2, P3, (), u'', R2_P3),
            (None, P3, (), u'', default_P3),
            ]
        expect.sort()
        self.assertEqual(got, expect)

    def test_getRegisteredMatching_for_and_provided_1(self):
        registry = self.getRegistry()

        got = list(registry.getRegisteredMatching(
            required = (R4, R12),
            provided = (P1, ),
            ))
        got.sort()
        expect = [
            (Interface, P3, (), u'', any_P3),
            (R2, P3, (), u'', R2_P3),
            (None, P3, (), u'', default_P3),
            ]
        expect.sort()
        self.assertEqual(got, expect)

    def test_getRegisteredMatching_for_and_provided_2(self):
        registry = self.getRegistry()

        got = list(registry.getRegisteredMatching(
            required = (R4, R12),
            provided = (P3, ),
            ))
        got.sort()
        expect = [
            (Interface, P3, (), u'', any_P3),
            (R2, P3, (), u'', R2_P3),
            (None, P3, (), u'', default_P3),
            ]
        expect.sort()
        self.assertEqual(got, expect)

    def test_getRegisteredMatching_for_and_provided_exact(self):
        registry = self.getRegistry()

        got = list(registry.getRegisteredMatching(
            required = (R2, ),
            provided = (P3, ),
            ))
        got.sort()
        expect = [
            (Interface, P3, (), u'', any_P3),
            (R2, P3, (), u'', R2_P3),
            (None, P3, (), u'', default_P3),
            ]
        expect.sort()
        self.assertEqual(got, expect)

    def test_pickling(self):
        from zope.component.tests.test_service import testServiceManager
        from zope.component.interfaces import IAdapterService
        testServiceManager.defineService('Adapters', IAdapterService)
        adapters = GlobalAdapterService()
        testServiceManager.provideService('Adapters', adapters)
        import pickle

        as = pickle.loads(pickle.dumps(adapters))
        self.assert_(as is adapters)

        testServiceManager._clear()

def test_suite():
    return unittest.makeSuite(GlobalAdapterServiceTests)
