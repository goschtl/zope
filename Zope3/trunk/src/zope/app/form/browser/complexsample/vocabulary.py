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

"""Sample vocabularies for use with the complexsample widgets.

$Id$
"""
from zope.interface.declarations import implements
from zope.schema.interfaces import ITokenizedTerm, IIterableVocabulary

from zope.app.form.browser.complexsample.interfaces import \
     ISampleVocabularyQuery, \
     IFancySampleVocabularyQuery, \
     ISampleVocabulary


class SampleTerm(object):
    implements(ITokenizedTerm)

    def __init__(self, value, title, keywords):
        self.value = value
        self.token = "tok%03d" % value
        self.title = title
        self.keywords = keywords
        self.group = groupNames[value % 3]

groupNames = {0: "1. first third",
              1: "2. second third",
              2: "3. final third"}


# XXX We could probably use more data, but creativity ebbs.
# title   keywords
TERM_DATA = '''\
Zero      alpha bravo
One       bravo charlie
Two       charlie david
Three     david bowie
Four      bowie clapton
Five      clapton guitar
Six       guitar drums
Seven     drums beat
Eight     beat rhythm
Nine      rhythm dance
Ten       dance steps
Eleven    stepping out
Twelve    on the floor
Thirteen  at the rave
Fourteen  bravo zope
Fifteen   twisty charlie
Sixteen   clapton cream
Seventeen cream pudding
Eighteen  dance pudding
Nineteen  barry plays drums
Twenty    dance on floor
'''

allTerms = []
for line in TERM_DATA.strip().split("\n"):
    parts = line.split()
    allTerms.append(SampleTerm(len(allTerms), parts[0], parts[1:]))
del line, parts


class SampleVocabularyQuery(object):

    implements(ISampleVocabularyQuery)

    def __init__(self, vocabulary):
        self.vocabulary = vocabulary

    def query(self, text):
        terms = text.split()
        if terms:
            L = []
            for term in self.vocabulary.terms:
                for t in terms:
                    if t not in term.keywords:
                        break
                else:
                    L.append(term)
        else:
            L = self.vocabulary.terms
        return SubsetSampleVocabulary(self.vocabulary, L)


class FancySampleVocabularyQuery(object):

    implements(IFancySampleVocabularyQuery)

    def __init__(self, vocabulary):
        self.vocabulary = vocabulary

    def query(self, text, group=None):
        L = SampleVocabularyQuery(self.vocabulary).query(text).terms
        if group is not None:
            L = [term for term in L if term.group == group]
        return SubsetSampleVocabulary(self.vocabulary, L)

    def getReferenceTypes(self):
        return self.vocabulary.allGroups


class SampleVocabulary(object):
    """A simple vocabulary."""

    implements(ISampleVocabulary)

    queryFactory = SampleVocabularyQuery

    def __init__(self, context=None):
        self.context = context
        self.terms = allTerms
        self.allGroups = []
        for term in self.terms:
            if term.group not in self.allGroups:
                self.allGroups.append(term.group)
        self.allGroups.sort()

    def __contains__(self, value):
        for term in self.terms:
            if value == term.value:
                return True
        return False

    def getQuery(self):
        return self.queryFactory(self)

    def getTerm(self, value):
        for term in self.terms:
            if term.value == value:
                return term
        raise LookupError(value)

    def getTermByToken(self, token):
        for term in self.terms:
            if term.token == token:
                return term
        raise LookupError(token)


class SubsetSampleVocabulary(SampleVocabulary):

    implements(ISampleVocabulary, IIterableVocabulary)

    def __init__(self, vocabulary, terms):
        self.vocabulary = vocabulary
        self.terms = terms
        self.allGroups = []
        for term in self.terms:
            if term.group not in self.allGroups:
                self.allGroups.append(term.group)
        self.allGroups.sort()

    def __iter__(self):
        return iter(self.terms)

    def __len__(self):
        return len(self.terms)
