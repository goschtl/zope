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
"""Unit tests for the global vocabulary service and ZCML integration.

$Id: test_vocabulary.py,v 1.5 2003/10/29 20:28:50 sidnei Exp $
"""
import unittest
from zope.app.schema.metaconfigure import \
     vocabulary as register, FactoryKeywordPasser
from zope.app.schema import vocabulary
from zope.app.tests.placelesssetup import PlacelessSetup


class MyContext:
    def resolve(self, name):
        return MyFactory

    def action(self, discriminator=None, callable=None, args=None, kw=None):
        self.discriminator = discriminator
        self.callable = callable
        self.args = args or ()
        self.kw = kw or {}


class MyFactory:
    def __init__(self, context, **kw):
        self.ob = context
        self.kw = kw


class VocabularyServiceTests(PlacelessSetup, unittest.TestCase):

    def test_global_missing_vocabulary(self):
        self.assertRaises(LookupError,
                          vocabulary.vocabularyService.get,
                          None, "missing-vocabulary")


    def check_vocabulary_get(self, kw={}):
        context = object()
        vocab = vocabulary.vocabularyService.get(context, "my-vocab")
        self.assert_(vocab.ob is context)
        self.assertEqual(vocab.kw, kw)

    extra_keywords = {"filter": "my-filter",
                      "another": "keyword"}

    def test_action_without_keywords(self):
        # make sure the action machinery works, aside from ZCML concerns
        context = MyContext()
        register(context, "my-vocab", MyFactory)
        # check our expectations of the action:
        self.assertEqual(len(context.args), 2)
        self.assertEqual(context.args[0], "my-vocab")
        self.failIf(isinstance(context.args[1], FactoryKeywordPasser))
        self.assertEqual(context.kw, {})
        context.callable(*context.args, **context.kw)
        # make sure the factory behaves as expected:
        self.check_vocabulary_get()

    def test_action_with_keywords(self):
        # make sure the action machinery works, aside from ZCML concerns
        context = MyContext()
        actions = register(context, "my-vocab", MyFactory,
                           **self.extra_keywords)
        # check our expectations of the action:
        self.assertEqual(len(context.args), 2)
        self.assertEqual(context.args[0], "my-vocab")
        self.assertEqual(context.kw, {})
        self.assert_(isinstance(context.args[1], FactoryKeywordPasser))
        # enact the registration:
        context.callable(*context.args, **context.kw)
        # make sure the factory behaves as expected:
        self.check_vocabulary_get(self.extra_keywords)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(VocabularyServiceTests),
        ))

if __name__ == '__main__':
    unittest.main()
