import grok
from zope import interface, schema
from isbn import isValidISBN, isValidISBN10, isValidISBN13
from isbn import convertISBN10toISBN13, convertISBN13toLang

import os

STATIC_PATH = os.path.join(os.path.dirname(__file__), 'static')

ARTICLES = {
    'en': u'the a an'.split(),
    'fr': u'le la les un une des'.split(),
    'de': (u'der das die den dem ein eine einen einem einer'
           u'kein keine keinen keiner').split(),
    'es': u'el los la las un unos una unas'.split(),
    'pt': u'o os a as um uns uma umas'.split(),
}

class IBook(interface.Interface):
    title = schema.TextLine(title=u"Title", required=True)
    isbn = schema.TextLine(title=u"ISBN", required=False,
                           constraint=isValidISBN,
                           description=u"ISBN in 10 or 13 digit format"
                           )
    creators = schema.List(title=u"Authors", required=False,
                           value_type=schema.TextLine(), default=[])
    edition = schema.TextLine(title=u"Edition", required=False)
    publisher = schema.TextLine(title=u"Publisher", required=False)
    issued = schema.TextLine(title=u"Issued", required=False)
    # TODO: set a vocabulary for language
    language = schema.TextLine(title=u"Language", required=False)

class Book(grok.Model):
    interface.implements(IBook)
    __title = ''        # = __main_title + __title_glue + __sub_title
    __main_title = ''   # title without sub-title
    __sub_title = ''    # sub-title: whatever comes after a ":" or the first "("
    __title_glue = ''   # may be either ":" or ""
    __filing_title = '' # title with article at end (for sorting and display)
    __isbn = ''     # the ISBN as entered by the user
    __isbn13 = ''   # ISBN-13, digits only (no dashes)
    __language = None

    def __init__(self, title=None, isbn13=None, creators=None, edition=None,
                 publisher=None, issued=None):
        super(Book, self).__init__()
        if isbn13:
            self.isbn13 = isbn13
        # Note: the title is set after the isbn13 so the language can be
        # guessed from the isbn13 and the __filing_title can be set
        self.title = title
        if creators is None:
            self.creators = []
        else:
            self.creators = creators
        self.edition = edition
        self.publisher = publisher
        self.issued = issued
        
    def getTitle(self):
        return self.__title

    def setTitle(self, title):
        self.__title = title
        self.setFilingTitle()
        
    title = property(getTitle, setTitle)

    def getISBN(self):
        return self.__isbn

    def setISBN(self, isbn):
        if isbn is None: return
        self.__isbn = isbn
        if isValidISBN13(isbn):
            self.__isbn13 = isbn
        elif isValidISBN10(isbn):
            self.__isbn13 = convertISBN10toISBN13(isbn)

    isbn = property(getISBN, setISBN)

    def getISBN13(self):
        if self.isbn and self.__isbn13 is None:
            self.setISBN13(self.isbn) #cache it
        return self.__isbn13

    def setISBN13(self, isbn):
        if isValidISBN13(isbn):
            self.__isbn13 = isbn
        elif isValidISBN10(isbn):
            self.__isbn13 = convertISBN10toISBN13(isbn)
        else:
            raise ValueError, '%s is not a valid ISBN-10 or ISBN-13' % isbn
        # if the isbn field is empty, fill it with the isbn13
        if not self.isbn:
            self.isbn = self.__isbn13

    isbn13 = property(getISBN13, setISBN13)

    def getShortTitle(self):
        if u':' in self.title:
            title = self.title.split(u':')[0].strip()
        else:
            title = self.title
        words = title.split()
        if words <= 7:
            return title
        else:
            return u' '.join(words[:7])+u'...'
        
    def splitTitle(self):
        if not self.__main_title:
            main_title = title = self.title.strip()
            sub_title = ''
            glue = ''
            pos_colon = title.find(u':')
            pos_paren = title.find(u'(')
            if pos_colon >= 0 and ((pos_paren >= 0 and pos_colon < pos_paren)
                or pos_paren < 0):
                main_title = title[:pos_colon]  
                sub_title =  title[pos_colon+1:] # exclude the colon
                glue = ':'
            elif pos_paren >= 0:
                main_title = title[:pos_paren]
                sub_title =  title[pos_paren:]
                glue = ''
            self.__main_title = main_title
            self.__title_glue = glue
            self.__sub_title = sub_title
        return (self.__main_title, self.__title_glue, self.__sub_title)
    
    def getLanguage(self):
        if not self.__language and self.__isbn13: # guess from ISBN
            self.__language = convertISBN13toLang(self.__isbn13)
        return self.__language
    
    def setLanguage(self, language):
        self.__language = language
        self.setFilingTitle()
        
    language = property(getLanguage, setLanguage)
                
    def getFilingTitle(self):
        if not self.__filing_title:
            self.setFilingTitle()
        return self.__filing_title
    
    def setFilingTitle(self, filing_title=None):
        if filing_title:
            self.__filing_title = filing_title
        else: # generate automatically
            # Do we know the language and it's articles?
            if self.language and self.language in ARTICLES:
                main_title, glue, sub_title = self.splitTitle()
                word0 = main_title.split()[0]
                if word0.lower() in ARTICLES[self.language]:
                    main_title = main_title[len(word0):].strip()+u', '+word0
                    if glue != u':': # need to add space after the article
                        main_title += u' '
                self.__filing_title = main_title + glue + sub_title
            else:
                self.__filing_title = self.title
    
    filing_title = property(getFilingTitle, setFilingTitle)

    def getMainTitle(self):
        if not self.__main_title:
            self.splitTitle()
        return self.__main_title
    
    main_title = property(getMainTitle)

    def getSubTitle(self):
        # Note: the __sub_title maybe empty even after a splitTitle,
        # so we check for the __main_title
        if not self.__main_title: 
            self.splitTitle()
        return self.__sub_title
    
    sub_title = property(getSubTitle)

    def creatorsLine(self):
        return '; '.join(self.creators)

class Edit(grok.EditForm):
    pass

class Index(grok.DisplayForm):
    pass

class Details(grok.View):
    
    def __init__(self, *args):
        # XXX: Is this super call really needed for a View sub-class?
        super(Details,self).__init__(*args)

        # Note: this method was created because calling context properties
        # from the template raises a traversal error
        self.main_title = self.context.main_title
        self.sub_title = self.context.sub_title
        self.isbn13 = self.context.isbn13
        
    def coverUrl(self):
        cover_name = 'covers/medium/'+self.context.__name__+'.jpg'
        return self.static.get(cover_name,
                               self.static['covers/small-placeholder.jpg'])()

    
