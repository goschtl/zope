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
"""Keyword catalog index

$Id:$
"""
import zope.index.keyword
import zope.interface

import zope.app.container.contained
import zope.app.catalog.attribute
import zope.app.catalog.interfaces

class IKeywordIndex(zope.app.catalog.interfaces.IAttributeIndex,
                     zope.app.catalog.interfaces.ICatalogIndex):
    """Interface-based catalog keyword index"""

class KeywordIndex(zope.app.catalog.attribute.AttributeIndex,
                    zope.index.keyword.KeywordIndex,
                    zope.app.container.contained.Contained):

    zope.interface.implements(IKeywordIndex)

class CaseInsensitiveKeywordIndex(zope.app.catalog.attribute.AttributeIndex,
                                      zope.index.keyword.CaseInsensitiveKeywordIndex,
                                      zope.app.container.contained.Contained):

    zope.interface.implements(IKeywordIndex)
