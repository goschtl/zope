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

$Id: vocabulary.py,v 1.8 2004/04/24 23:19:52 srichter Exp $
"""
from zope.interface import implements
from zope.proxy import removeAllProxies
from zope.schema.interfaces import \
     ITokenizedTerm, IVocabulary, IVocabularyTokenized
from zope.schema.vocabulary import getVocabularyRegistry
from zope.component.interfaces import IFactory

from zope.app import zapi
from zope.app.form.browser import DropdownWidget
from zope.app.renderer.interfaces import ISource

class ISourceTypeVocabulary(IVocabulary, IVocabularyTokenized):
    """Marker interface, so we can register a special widget for it."""

class SourceTypeTerm:

    implements(ITokenizedTerm)

    def __init__(self, name, factory):
        self.token = self.value = name
        self.title = factory.title
        self.description = factory.description


class SourceTypeVocabulary(object):

    implements(IVocabulary, IVocabularyTokenized)

    def __init__(self, context):
        self.types = list(zapi.getFactoriesFor(None, ISource))

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


class SourceTypeEditWidget(DropdownWidget):

    def textForValue(self, term):
        return term.title
