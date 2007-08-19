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
"""Kirbi book exemplar class
"""

import grok
from interfaces import IItem, ILease
from zope.interface import Interface, implements, invariant
from zope import schema
from datetime import datetime

class Item(grok.Container):
    """An exemplar of a book.
    
    See note at interfaces.IItem.
    """

    implements(IItem)
    
    def __init__(self, manifestation, description=u'', catalog_datetime=None):
        super(Item, self).__init__()
        self.manifestation = manifestation
        self.description = description
        if catalog_datetime is None:
            self.catalog_datetime = datetime.now()
            