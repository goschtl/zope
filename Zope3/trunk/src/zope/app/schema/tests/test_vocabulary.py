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

"""Unit tests for the global vocabulary service and ZCML integration."""

import unittest

from zope.app.schema import vocabulary
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.configuration import xmlconfig


class MyContext:
    def resolve(self, name):
        return MyFactory

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

    def load_zcml(self, fragment):
        xmlconfig.string("""\
        <zopeConfigure xmlns='http://namespaces.zope.org/zope'>
          <include package='zope.configuration' file='meta.zcml' />
          <include package='zope.app.component' file='meta.zcml' />
          <include package='zope.app.schema' file='meta.zcml' />

          <include package='zope.app.schema' />

          %s
        </zopeConfigure>
        """ % fragment)

    extra_keywords = {"filter": "my-filter",
                      "another": "keyword"}

    def test_simple_zcml(self):
        self.load_zcml("""\
          <vocabulary
              name='my-vocab'
              factory='zope.app.schema.tests.test_vocabulary.MyFactory'
              />""")
        self.check_vocabulary_get()

    def test_passing_keywords_from_zcml(self):
        self.load_zcml("""\
          <vocabulary
              name='my-vocab'
              factory='zope.app.schema.tests.test_vocabulary.MyFactory'
              filter='my-filter'
              another='keyword'
              />""")
        self.check_vocabulary_get(self.extra_keywords)

    def test_action_without_keywords(self):
        # make sure the action machinery works, aside from ZCML concerns
        actions = vocabulary.register(MyContext(), "my-vocab", ".maker")
        self.assertEqual(len(actions), 1)
        descriminator, callable, args, kw = actions[0]
        # check our expectations of the action:
        self.assertEqual(len(args), 2)
        self.assertEqual(args[0], "my-vocab")
        self.assertEqual(kw, {})
        self.failIf(isinstance(args[1], vocabulary.FactoryKeywordPasser))
        # enact the registration:
        callable(*args, **kw)
        # make sure the factory behaves as expected:
        self.check_vocabulary_get()

    def test_action_with_keywords(self):
        # make sure the action machinery works, aside from ZCML concerns
        actions = vocabulary.register(MyContext(), "my-vocab", ".maker",
                                      **self.extra_keywords)
        self.assertEqual(len(actions), 1)
        descriminator, callable, args, kw = actions[0]
        # check our expectations of the action:
        self.assertEqual(len(args), 2)
        self.assertEqual(args[0], "my-vocab")
        self.assertEqual(kw, {})
        self.assert_(isinstance(args[1], vocabulary.FactoryKeywordPasser))
        # enact the registration:
        callable(*args, **kw)
        # make sure the factory behaves as expected:
        self.check_vocabulary_get(self.extra_keywords)


def test_suite():
    return unittest.makeSuite(VocabularyServiceTests)

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
