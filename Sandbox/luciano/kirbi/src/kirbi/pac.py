import grok
from book import Book, IBook
from zope.app.container.contained import NameChooser as BaseNameChooser
from zope.app.container.interfaces import INameChooser
from zope.interface import implements
from zope import event
from zope.lifecycleevent import ObjectModifiedEvent, Attributes
from zope import schema
from operator import attrgetter
from isbn import isValidISBN, isValidISBN10, convertISBN10toISBN13, filterDigits

from zope.app.catalog.interfaces import ICatalog
from zope.component import getUtility, queryUtility
from persistent.dict import PersistentDict
from time import localtime, strftime

class Pac(grok.Container):
    """ Pac (public access catalog)

        Bibliographic records for all items (books, disks etc.) known to this
        Kirbi instance. The contents of this catalog is public, but information
        about item ownership and availability is not kept here.

        In library science the term "catalog" is used to refer to
        "a comprehensive list of the materials in a given collection".
        The Pac name was chosen to avoid confusion with zc.catalog.
        The Pac is not an instance of a Zope catalog, but will use one.
    """

    def __init__(self):
        super(Pac, self).__init__()
        # books with isbn but no title
        self.incomplete_isbns = PersistentDict()
        # isbns sent for fetching
        self.pending_isbns = PersistentDict()

    def addBook(self, book):
        name = INameChooser(self).chooseName(book.isbn13, book)
        self[name] = book
        return book.__name__

    def getIncomplete(self):
        return self.incomplete_isbns

    def addIncomplete(self, isbn13):
        timestamp = strftime('%Y-%m-%d %H:%M:%S',localtime())
        self.incomplete_isbns[isbn13] = timestamp

    def getPending(self):
        return self.pending_isbns

    def dumpIncomplete(self):
        dump = list(self.incomplete_isbns)
        self.pending_isbns.update(self.incomplete_isbns)
        self.incomplete_isbns.clear()        
        return dump
    
    def retryPending(self, isbns):
        for isbn13 in isbns:
            if isbn13 in self.pending_isbns:
                self.incomplete_isbns[isbn13] = self.pending_isbns[isbn13]
                del self.pending_isbns[isbn13]

    def updateBooks(self, book_dict_list):                
        updated = 0
        for book_dict in book_dict_list:
            isbn13 = book_dict.get('isbn13')
            if isbn13 not in self.pending_isbns:
                msg = '%s not in pending ISBNs; update not allowed.' % isbn13
                raise LookupError, msg
            if isbn13 in self:
                book = self[isbn13]
                book.update(**book_dict)
                del self.pending_isbns[isbn13]
                changed = Attributes(IBook, *list(book_dict))
                event.notify(ObjectModifiedEvent(book, changed))
                updated += 1
        return updated
            
@grok.subscribe(Book, grok.IObjectAddedEvent)
def bookAdded(book, event):
    if not book.title and book.isbn13:
        pac = book.__parent__
        pac.addIncomplete(book.isbn13)

class Incomplete(grok.View):
    def sortedByTime(self, isbn_dict):
        pairs = ((timestamp, isbn) for isbn, timestamp in
                    isbn_dict.items())
        return (dict(timestamp=timestamp,isbn=isbn)
                for timestamp, isbn in sorted(pairs))
            
    def incompleteIsbns(self):
        return list(self.sortedByTime(self.context.getIncomplete()))

    def pendingIsbns(self):
        return list(self.sortedByTime(self.context.getPending()))
    
    def update(self, isbns=None):
        if isbns:
            self.context.retryPending(isbns)
        if self.context.getIncomplete() or self.context.getPending():
            self.request.response.setHeader("Refresh", "5; url=%s" % self.url())
        


class Index(grok.View):

    def update(self, query=None):
        if not query:
            # XXX: if the query is empty, return all books; this should change
            # to some limited default search criteria or none at all
            results = self.context.values()
            self.results_title = 'All items'
        else:
            query = query.strip()
            catalog = getUtility(ICatalog)
            if query.startswith(u'cr:'):
                query = query[3:].strip().lower()
                set_query = {'any_of': [query]}
                results = catalog.searchResults(creatorsSet=set_query)
            elif isValidISBN(query):
                isbn = filterDigits(query)
                if len(isbn) == 10:
                    isbn = convertISBN10toISBN13(isbn)
                results = catalog.searchResults(isbn13=(isbn,isbn))
            else:
                results = catalog.searchResults(searchableText=query)
            # Note: to sort the results, we must cast the result iterable
            # to a list, which can be very expensive
            results = list(results)
            if len(results) == 0:
                qty = u'No i'
                s = u's'
            elif len(results) == 1:
                qty = u'I'
                s = u''
                self.redirect(self.url(results[0])+'/details')
            else:
                qty = u'%s i' % len(results)
                s = u's'
            self.results_title = u'%stem%s matching "%s"' % (qty, s, query)

        self.results = sorted(results, key=attrgetter('filing_title'))

    def coverUrl(self, book):
        cover_name = 'covers/large/'+book.isbn13+'.jpg'
        return self.static.get(cover_name,
                               self.static['covers/small-placeholder.jpg'])()

class AddBook(grok.AddForm):

    form_fields = grok.AutoFields(Book)

    @grok.action('Add book')
    def add(self, **data):
        book = Book()
        self.applyData(book, **data)
        self.context.addBook(book)
        self.redirect(self.url(self.context))
        
class AddBooks(grok.View):
    
    invalid_isbns = []
    
    def update(self, isbns=None):
        if isbns is not None:
            isbns = list(set(isbns.split()))
            self.invalid_isbns = []
            for isbn in isbns:
                if isValidISBN(isbn):
                    book = Book(isbn=isbn)
                    if book.isbn13 not in self.context:
                        self.context.addBook(book)
                else:
                    self.invalid_isbns.append(isbn)
                    
    def invalidISBNs(self):
        if self.invalid_isbns:
            return '\n'.join(self.invalid_isbns)
        else:
            return ''

class NameChooser(grok.Adapter, BaseNameChooser):
    implements(INameChooser)

    def nextId(self,fmt='%s'):
        """ Binary search to quickly find an unused numbered key, useful
            when importing many books without ISBN. The algorithm generates a
            key right after the largest numbered key or in some unused lower
            numbered slot found by the second loop. If keys are later deleted
            in random order, some of the resulting slots will be reused and
            some will not.
        """
        i = 1
        while fmt%i in self.context:
            i *= 2
        blank = i
        full = i//2
        while blank > (full+1):
            i = (blank+full)//2
            if fmt%i in self.context:
                full = i
            else:
                blank = i
        return fmt%blank

    def chooseName(self, name, object):
        name = name or self.nextId('k%04d')
        # Note: potential concurrency problems of nextId are (hopefully)
        # handled by calling the super.NameChooser
        return super(NameChooser, self).chooseName(name, object)

class PacRPC(grok.XMLRPC):

    def list(self):
        return list(self.context)

    def add(self, book_dict):
        book = Book(**book_dict)
        return self.context.addBook(book)

    def updateBooks(self, book_dict_list):
        return self.context.updateBooks(book_dict_list)

    def dumpIncomplete(self):
        return self.context.dumpIncomplete()



class ImportDemo(grok.View):

    def render(self):
        from demo.collection import collection
        for record in collection:
            if record['name']:
                record['creators'] = [creator.strip() for creator in record['name'].split('|')]
                del record['name']
            for key in record.keys():
                if record[key] is None:
                    del record[key]
            book = Book(**record)
            self.context.addBook(book)

        self.redirect(self.url('index'))
