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
"""Testing vocabulary directive.

$Id: test_directives.py,v 1.2 2003/08/17 06:07:58 philikon Exp $
"""
import unittest

from zope.component.tests.placelesssetup import PlacelessSetup
from zope.configuration import xmlconfig
from zope.app.schema import vocabulary

import zope.app.schema


class DirectivesTest(PlacelessSetup, unittest.TestCase):

    extra_keywords = {"filter": "my-filter",
                      "another": "keyword"}

    def check_vocabulary_get(self, kw={}):
        context = object()
        vocab = vocabulary.vocabularyService.get(context, "my-vocab")
        self.assert_(vocab.ob is context)
        self.assertEqual(vocab.kw, kw)

    def test_simple_zcml(self):
        self.context = xmlconfig.file("tests/simple_vocab.zcml",
                                      zope.app.schema)
        self.check_vocabulary_get()

    def test_passing_keywords_from_zcml(self):
        self.context = xmlconfig.file("tests/keywords_vocab.zcml",
                                      zope.app.schema)
        self.check_vocabulary_get(self.extra_keywords)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(DirectivesTest),
        ))

if __name__ == '__main__':
    unittest.main()
