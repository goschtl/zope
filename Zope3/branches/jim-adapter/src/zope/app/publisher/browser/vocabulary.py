##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Browser vocabularies

$Id$
"""
from zope.interface import classProvides
from zope.publisher.interfaces.browser import IBrowserSkinType
from zope.app.component.vocabulary import UtilityVocabulary
from zope.app.schema.interfaces import IVocabularyFactory

class BrowserSkinsVocabulary(UtilityVocabulary):
    classProvides(IVocabularyFactory)
    interface = IBrowserSkinType
