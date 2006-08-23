##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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

"""
$Id$
"""
__docformat__ = 'restructuredtext'

import unittest

import zope.interface
import zope.component
from zope.app.testing import ztapi

from zope.i18n.interfaces import IUserPreferredLanguages

from z3c.language.session.interfaces import ILanguageSession
from z3c.language.negotiator.app import Negotiator


class TestLanguageSession(object):
    
    zope.interface.implements(ILanguageSession)
    zope.component.adapts(IUserPreferredLanguages)

    def __init__(self, request):
        pass

    def getLanguage(self):
        return 'fr'


class Env(object):
    zope.interface.implements(IUserPreferredLanguages)

    def __init__(self, langs=()):
        self.langs = langs

    def getPreferredLanguages(self):
        return self.langs


class NegotiatorTest(zope.component.testing.PlacelessSetup, 
    unittest.TestCase):

    def setUp(self):
        super(NegotiatorTest, self).setUp()
        self.negotiator = Negotiator()
        zope.component.provideAdapter(TestLanguageSession)

    def test__getLanguagePolicy(self):
        default = 'session --> browser --> server'
        self.assertEqual(self.negotiator._getLanguagePolicy(), default)

    def test__setLanguagePolicy(self):
        self.negotiator.policy = 'server'
        self.assertEqual(self.negotiator.policy, 'server')
        self.assertRaises(
            ValueError, self.negotiator._setLanguagePolicy, 'undefined')

    def test_policy(self):
        default = 'session --> browser --> server'
        self.assertEqual(self.negotiator.policy, default)
        self.negotiator.policy = 'server'
        self.assertEqual(self.negotiator.policy, 'server')

    def test_serverLanguage(self):
        self.assertEqual(self.negotiator.serverLanguage, None)
        self.negotiator.serverLanguage = 'de'
        self.assertEqual(self.negotiator.serverLanguage, 'de')

    def test_sessionLanguages(self):
        self.assertEqual(self.negotiator.sessionLanguages, [])
        self.negotiator.sessionLanguages = ['de', 'en']
        self.assertEqual(self.negotiator.sessionLanguages, ['de', 'en'])

    def test_offeredLanguages(self):
        self.assertEqual(self.negotiator.offeredLanguages, [])
        self.negotiator.offeredLanguages = ['de', 'en']
        self.assertEqual(self.negotiator.offeredLanguages, ['de', 'en'])

    def test_getLanguages(self):
        # first set the default policy to 'browser'
        self.negotiator.policy = 'browser'
        self.assertEqual(self.negotiator.policy, 'browser')

        _cases = (
            (('en','de'), ('en','de','fr'),  'en'),
            (('en'),      ('it','de','fr'),  None),
            (('pt-br','de'), ('pt_BR','de','fr'),  'pt_BR'),
            (('pt-br','en'), ('pt', 'en', 'fr'),  'pt'),
            (('pt-br','en-us', 'de'), ('de', 'en', 'fr'),  'en'),
            )

        for user_pref_langs, obj_langs, expected in _cases:
            env = Env(user_pref_langs)
            self.assertEqual(self.negotiator.getLanguage(obj_langs, env),
                             expected)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(NegotiatorTest),
                           ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
