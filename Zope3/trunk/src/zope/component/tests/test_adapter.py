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

        registry.provideAdapter(None, P3, [default_P3])
        registry.provideAdapter(Interface, P3, [any_P3])
        registry.provideAdapter(R2, P3, [R2_P3])

        return registry
    
    def test_getRegisteredMatching_all(self):
        registry = self.getRegistry()

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
        registry = self.getRegistry()

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
        registry = self.getRegistry()

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
        registry = self.getRegistry()

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
        registry = self.getRegistry()

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
        registry = self.getRegistry()

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
        registry = self.getRegistry()

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
        registry = self.getRegistry()

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
    return unittest.makeSuite(GlobalAdapterServiceTests)
