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
from interfaces import IItem, IBook
from zope.interface import Interface, implements, invariant
from zope import schema
from datetime import datetime

class Item(grok.Container):
    """An exemplar of a book.

    See note at interfaces.IItem.

    >>> it = Item('','Nobody')
    >>> IItem.providedBy(it)
    True

    Now let's make it provide IBook.

    >>> from kirbi.book import Book
    >>> book = Book('Any Book')
    >>> it.manifestation = book

    >>> IBook.providedBy(it)
    True

    """

    implements(IItem, IBook)

    def __init__(self, manifestation_id, owner_id, description=u'',
                 catalog_datetime=None):
        super(Item, self).__init__()
        self.manifestation_id = manifestation_id
        if manifestation_id:
            self.manifestation = grok.getSite()['pac'].get(manifestation_id)
        self.description = description
        self.owner_id = owner_id
        if catalog_datetime is None:
            self.catalog_datetime = datetime.now()

    def getCoverId(self):
        return self.manifestation.__name__

    def __getattr__(self,name):
        # XXX: Martijn Faassen sugests a refactoring here, implementing
        # the Item->Manifestation relationship not using this sort of
        # dynamically hacked inheritance but in as an association
        return getattr(self.manifestation, name)
