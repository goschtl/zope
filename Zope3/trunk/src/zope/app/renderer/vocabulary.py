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

$Id: vocabulary.py,v 1.5 2004/03/14 01:11:39 srichter Exp $
"""
from zope.interface import implements
from zope.proxy import removeAllProxies
from zope.schema.interfaces import \
     ITokenizedTerm, IVocabulary, IVocabularyTokenized
from zope.component.interfaces import IFactory

from zope.app import zapi
from zope.app.form.browser.vocabularywidget import DropdownListWidget
from zope.app.renderer.interfaces import ISource

class SourceTypeTerm:

    implements(ITokenizedTerm)

    def __init__(self, name, factory):
        self.token = self.value = name
        self.title = factory.title
        self.description = factory.description


class SourceTypeVocabulary(object):

    implements(IVocabulary, IVocabularyTokenized)

    def __init__(self, context):
        self.types = zapi.getFactoriesFor(None, ISource)

    def __contains__(self, value):
        return value in [name for name, fact in self.types]

    def __iter__(self):
        return iter([SourceTypeTerm(name, fact) for name, fact in self.types])

    def __len__(self):
        return len(self.types)

    def getQuery(self):
        return None

    def getTerm(self, value):
        for name, fact in self.types:
            if name == value:
                return SourceTypeTerm(name, fact)

        raise KeyError, 'item (%s) not in vocabulary.' %value

    def getTermByToken(self, token):
        return self.getTerm(token)


class SourceTypeEditWidget(DropdownListWidget):

    def __init__(self, field, request):
        self.request = request
        vocabs = zapi.getService(field, "Vocabularies")
        self.vocabulary = vocabs.get(field, "SourceTypes")
        self.setField(field)

    def textForValue(self, term):
        return term.title
