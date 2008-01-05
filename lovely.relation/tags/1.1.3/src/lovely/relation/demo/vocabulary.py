##############################################################################
#
# Copyright (c) 2006-2007 Lovely Systems and Contributors.
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
__docformat__ = "reStructuredText"

from zope.schema.vocabulary import SimpleVocabulary
from interfaces import IDocument

def documentsInParentVocabulary(context):

    """a vocabulary that returns the child documents __name__for any
    subobjects of parent"""

    return SimpleVocabulary.fromItems(
        [(k, v) for k, v in context.__parent__.items() \
         if IDocument.providedBy(v)])

