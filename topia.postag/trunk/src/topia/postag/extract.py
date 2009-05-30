##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""POS Tagger

$Id$
"""
import zope.interface

from topia.postag import interfaces, tag

SEARCH = 0
NOUN = 1

def defaultFilter(word, occur, strength):
    return ((strength == 1 and occur >= 3) or
            (strength >= 2))

def _add(term, norm, keyword, keywords):
    keyword.append((term, norm))
    keywords.setdefault(norm, 0)
    keywords[norm] += 1

class KeywordExtractor(object):
    zope.interface.implements(interfaces.IKeywordExtractor)

    def __init__(self, tagger=None, filter=defaultFilter):
        if tagger is None:
            tagger = tag.Tagger()
            tagger.initialize()
        self.tagger = tagger
        self.filter = filter

    def extract(self, terms):
        """See interfaces.IKeywordExtractor"""
        keywords = {}
        # Phase 1: A little state machine is used to build simple and
        # composite keywords.
        keyword = []
        state = SEARCH
        while terms:
            term, tag, norm = terms.pop(0)
            if state == SEARCH and tag.startswith('N'):
                state = NOUN
                _add(term, norm, keyword, keywords)
            elif state == SEARCH and tag == 'JJ' and term[0].isupper():
                state = NOUN
                _add(term, norm, keyword, keywords)
            elif state == NOUN and tag.startswith('N'):
                _add(term, norm, keyword, keywords)
            elif state == NOUN and tag == 'JJ' and term[0].isupper():
                _add(term, norm, keyword, keywords)
            elif state == NOUN and not tag.startswith('N'):
                state = SEARCH
                if len(keyword) > 1:
                    word = ' '.join([word for word, norm in keyword])
                    keywords.setdefault(word, 0)
                    keywords[word] += 1
                keyword = []
        # Phase 2: Only select the keywords that fulfill the filter criteria.
        # Also create the keyword strength.
        return [
            (word, occur, len(word.split()))
            for word, occur in keywords.items()
            if self.filter(word, occur, len(word.split()))]

    def __call__(self, text):
        """See interfaces.IKeywordExtractor"""
        terms = self.tagger(text)
        return self.extract(terms)

    def __repr__(self):
        return '<%s using %r>' %(self.__class__.__name__, self.tagger)
