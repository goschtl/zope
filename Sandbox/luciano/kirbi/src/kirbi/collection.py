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
from zope.app.container.interfaces import INameChooser

class Collection(grok.Container):
    """A collection of items (books, disks etc.) belonging to one user.
    
    >>> myCollection = Collection('123')
    >>> ICollection.providedBy(myCollection)
    True
    
    """
    implements(ICollection)
    def __init__(self, title, private=False):
        super(Collection, self).__init__()
        self.title = title
        self.private = False ### XXX: implement private collections
        
    def addItem(self, item):
        name = INameChooser(self).chooseName('', item)
        self[name] = item
        return item.__name__
        
        
class Index(grok.View):
    grok.context(Collection)

    def __init__(self, context, request):
        super(Index, self).__init__(context, request)
        self.pac = grok.getSite()['pac']

    def update(self, query=None):
        results = self.context.values()
        self.results_title = 'All items'
        self.results = results
        
    def coverUrl(self, item):
        book = self.pac[item.manifestation_id]
        cover_name = 'covers/large/'+book.__name__+'.jpg'
        return self.static.get(cover_name,
                               self.static['covers/small-placeholder.jpg'])()
        

class AddBookItems(grok.View):

    invalid_isbns = []

    def update(self, isbns=None, retry_isbns=None, refreshed=False):
        self.pac = grok.getSite()['pac']
        self.invalid_isbns = []
        if isbns is not None:
            if isinstance(isbns, basestring):
                isbns = isbns.split()
            for isbn in set(isbns): #use set to remove duplicates
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
            if len(isbns) > len(self.invalid_isbns):
                added = True

        if retry_isbns:
            self.context.retryPending(retry_isbns)
        # XXX this would be great with AJAX, avoiding the ugly refresh
        # If there are no invalid_isbns in the text area, set refresh or redirect
        if not self.invalid_isbns:
            if self.pac.getIncomplete() or self.pac.getPending():
                # Refresh page while there are pending books
                self.request.response.setHeader("Refresh", "5; url=%s?refreshed=1" % self.url())
            elif refreshed:
                # Redirect to collection if nothing is pending and we came from
                # a refresh (i.e. this is not the first visit to the form)
                self.redirect(self.url(self.context))

    def getInvalidISBNs(self):
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

class ImportSample(grok.View):
                
    def render(self, quantity=10):
        from demo.collection import collection
        from random import shuffle
        isbns = [book['isbn13'] for book in collection]
        shuffle(isbns)
        adder = AddBookItems(self.context, self.request)
        adder.update(isbns[:quantity])
        self.redirect(self.url('addbookitems'))

    

