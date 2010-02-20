##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
from z3c.optionstorage.vocabulary import OptionStorageVocabulary
from zope.component.zcml import utility
from zope.schema.interfaces import IVocabularyFactory


def optionStorageVocabulary(_context, name):
    def factory(object, name=name):
        return OptionStorageVocabulary(object, name=name)
    directlyProvides(factory, IVocabularyFactory)
    utility(_context, IVocabularyFactory, factory, name=name)
