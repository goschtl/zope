##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""

$Id$
"""
from zope import interface
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from z3ext.skintool import tool


class Vocabulary(SimpleVocabulary):

    def getTerm(self, value):
        try:
            return self.by_value[value]
        except KeyError:
            return self.by_value[self.by_value.keys()[0]]


class SkinsVocabulary(object):
    interface.implements(IVocabularyFactory)

    def __call__(self, context):
        terms = []
        for layer, info in tool.skins_registry.items():
            terms.append((info[2], info[1]))

        terms.sort()
        return Vocabulary(
            [SimpleTerm(name,name,title) for title, name in terms])


class LayersVocabulary(object):
    interface.implements(IVocabularyFactory)

    def __call__(self, context):
        terms = []
        for layer, info in tool.layers_registry.items():
            terms.append((info[2], info[1]))

        terms.sort()
        return Vocabulary(
            [SimpleTerm(name,name,title) for title, name in terms])
