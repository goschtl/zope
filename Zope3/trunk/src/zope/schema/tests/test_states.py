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

"""Tests of the states example."""

import unittest

from zope.interface import Interface

from zope.schema import vocabulary
from zope.schema.tests import states


class IBirthInfo(Interface):
    state1 = vocabulary.VocabularyField(
        title=u'State of Birth',
        description=u'The state in which you were born.',
        vocabulary="states",
        default="AL",
        )
    state2 = vocabulary.VocabularyField(
        title=u'State of Birth',
        description=u'The state in which you were born.',
        vocabulary="states",
        default="AL",
        )
    state3 = vocabulary.VocabularyField(
        title=u'Favorite State',
        description=u'The state you like the most.',
        vocabulary=states.StateVocabulary(),
        )
    state4 = vocabulary.VocabularyField(
        title=u"Name",
        description=u"The name of your new state",
        vocabulary="states",
        )

class BirthInfo:
    __implements__ = IBirthInfo

    def __init__(self):
        self.state = state


class StateSelectionTest(unittest.TestCase):
    def setUp(self):
        vocabulary._clear()
        vr = vocabulary.getVocabularyRegistry()
        vr.register("states", states.StateVocabulary)

    def tearDown(self):
        vocabulary._clear()

    def test_default_presentation(self):
        field = IBirthInfo.getDescriptionFor("state1")
        bound = field.bind(object())
        self.assertEqual(bound.vocabulary.getTerm("VA").title, "Virginia")

    def test_contains(self):
        vocab = states.StateVocabulary()
        count = 0
        L = list(vocab)
        for term in L:
            count += 1
            self.assert_(term.value in vocab)
        self.assertEqual(count, len(vocab))
        # make sure we get the same values the second time around:
        L = [term.value for term in L]
        L.sort()
        L2 = [term.value for term in vocab]
        L2.sort()
        self.assertEqual(L, L2)

    def test_prebound_vocabulary(self):
        field = IBirthInfo.getDescriptionFor("state3")
        bound = field.bind(None)
        self.assert_(bound.vocabularyName is None)
        self.assert_("AL" in bound.vocabulary)


def test_suite():
    return unittest.makeSuite(StateSelectionTest)

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
