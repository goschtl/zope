##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Vocabulary for the Source Type Registry

$Id: vocabulary.py,v 1.2 2003/10/29 20:26:28 sidnei Exp $
"""
from zope.interface import implements
from zope.component import getService
from zope.schema.interfaces import \
     ITokenizedTerm, IVocabulary, IVocabularyTokenized

class SourceTypeTerm:

    implements(ITokenizedTerm)

    def __init__(self, title):
        self.value = self.token = title
        self.title = title


class SourceTypeVocabulary(object):

    implements(IVocabulary, IVocabularyTokenized)

    def __init__(self, context):
        self.types = getService(context, 'SourceTypeRegistry')

    def __contains__(self, value):
        return value in self.types.getAllTitles()

    def __iter__(self):
        terms = map(lambda st: SourceTypeTerm(st), self.types.getAllTitles())
        return iter(terms)

    def __len__(self):
        return len(self.types.getAllTitles())

    def getQuery(self):
        return None

    def getTerm(self, value):
        if value not in self:
            raise KeyError, 'item (%s) not in vocabulary.' %value
        return SourceTypeTerm(value)

    def getTermByToken(self, token):
        if token not in self:
            raise KeyError, 'item (%s) not in vocabulary.' %token
        return self.getTerm(token)
