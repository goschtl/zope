##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""This is a keyword index which can be subscribed to an event service.

$Id: index.py,v 1.3 2003/08/17 06:06:54 philikon Exp $
"""

from zope.index.keyword.index import KeywordIndex 
from zope.interface import implements

from zope.app.interfaces.index.keyword import IUIKeywordCatalogIndex
from zope.app.interfaces.catalog.index import ICatalogIndex
from zope.app.index import InterfaceIndexingSubscriber

class KeywordCatalogIndex(InterfaceIndexingSubscriber, KeywordIndex):
    implements(ICatalogIndex, IUIKeywordCatalogIndex)

