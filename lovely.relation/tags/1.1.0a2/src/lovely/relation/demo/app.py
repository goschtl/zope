##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
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

from zope import interface
from persistent import Persistent
from zope.app.container.contained import Contained
from interfaces import IDocument, IRelatedByDocument
from lovely.relation.property import FieldRelationManager
from lovely.relation.property import RelationPropertyIn
from lovely.relation.property import RelationPropertyOut

documentRelated = FieldRelationManager(IDocument['related'],
                                       IRelatedByDocument['backrefs'],
                                       relType='demo.documentRelated')

class Document(Persistent, Contained):
    interface.implements(IDocument)

    related = RelationPropertyOut(documentRelated)
    backrefs = RelationPropertyIn(documentRelated)

