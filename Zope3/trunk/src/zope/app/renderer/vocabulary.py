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

$Id: vocabulary.py,v 1.3 2004/03/02 14:24:45 srichter Exp $
"""
from zope.interface import implements
from zope.proxy import removeAllProxies
from zope.schema.interfaces import \
     ITokenizedTerm, IVocabulary, IVocabularyTokenized

from zope.app import zapi
from zope.app.browser.form.vocabularywidget import DropdownListWidget
from zope.app.services.servicenames import Factories
from zope.app.renderer.interfaces import ISource

class SourceTypeTerm:

    implements(ITokenizedTerm)

    def __init__(self, name, info):
        self.token = self.value = name
        self.title = info.title
        self.description = info.description


class SourceTypeVocabulary(object):

    implements(IVocabulary, IVocabularyTokenized)

    def __init__(self, context):
        factories = zapi.getService(context, Factories)
        self.types = [(name, factories.getFactoryInfo(name)) \
                      for name, fact in factories.queryFactoriesFor(ISource,
                                                                    ())]
    def __contains__(self, value):
        return value in [name for name, info in self.types]

    def __iter__(self):
        return iter([SourceTypeTerm(name, info) for name, info in self.types])

    def __len__(self):
        return len(self.types)

    def getQuery(self):
        return None

    def getTerm(self, value):
        for name, info in self.types:
            if name == value:
                return SourceTypeTerm(name, info)

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
