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
"""Kirbi item collection
"""

import grok
from interfaces import ICollection
from zope.interface import implements
from kirbi.interfaces import IBook
from kirbi.isbn import toISBN13, InvalidISBN
from kirbi.item import Item
from kirbi.book import Book

class Collection(grok.Container):
    implements(ICollection)
    def __init__(self, title, private=False):
        super(Collection, self).__init__()
        self.title = title
        self.private = False ### XXX: implement private collections
        
    def addItem(self, item):
        name = INameChooser(self).chooseName(book.isbn13, book)
        self[name] = book
        return book.__name__
        
        
class Index(grok.View):
    def update(self, query=None):
        if not query:
            # XXX: if the query is empty, return all books; this should change
            # to some limited default search criteria or none at all
            results = self.context.values()
            self.results_title = 'All items'
        self.results = results

class AddBookItems(grok.View):
    grok.context(Collection)

    invalid_isbns = []

    def update(self, isbns=None, retry_isbns=None):
        self.pac = self.context.__parent__.__parent__['pac']
        self.invalid_isbns = []
        if isbns is not None:
            isbns = list(set(isbns.split()))
            for isbn in isbns:
                try:
                    isbn13 = toISBN13(isbn)
                except InvalidISBN:
                    self.invalid_isbns.append(isbn)
                    continue
                if isbn13 in self.pac:
                    book = self.pac[isbn13]
                else:
                    book = Book(isbn13=isbn13)
                    self.pac.addBook(book)
                    item = Item(book.__name__)
                    self.context.addItem(item)

        if retry_isbns:
            self.context.retryPending(retry_isbns)
        # XXX this would be great with AJAX, avoiding the ugly refresh
        if (not self.invalid_isbns) and (self.pac.getIncomplete()
                                         or self.pac.getPending()):
            self.request.response.setHeader("Refresh", "5; url=%s" % self.url())

    def invalidISBNs(self):
        if self.invalid_isbns:
            return '\n'.join(self.invalid_isbns)
        else:
            return ''

    def sortedByTime(self, isbn_dict):
        pairs = ((timestamp, isbn) for isbn, timestamp in
                    isbn_dict.items())
        return (dict(timestamp=timestamp,isbn=isbn)
                for timestamp, isbn in sorted(pairs))

    def incompleteIsbns(self):
        self.pac = self.context.__parent__.__parent__['pac']
        return list(self.sortedByTime(self.pac.getIncomplete()))

    def pendingIsbns(self):
        self.pac = self.context.__parent__.__parent__['pac']
        return list(self.sortedByTime(self.pac.getPending()))


    

