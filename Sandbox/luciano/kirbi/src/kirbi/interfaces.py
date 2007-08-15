from zope.interface import Interface, invariant, Invalid
from zope import schema
from isbn import isValidISBN

class IUser(Interface):
    """A Kirbi user"""
    login = schema.TextLine(title=u"Login",
                            required=True)
    name = schema.TextLine(title=u"Name",
                            required=False)
    password = schema.Password(title=u"Password",
                            required=True)

class InvalidISBN(schema.ValidationError):
    """This is not a valid ISBN-10 or ISBN-13"""

def validateISBN(isbn):
    if not isValidISBN(isbn):
        raise InvalidISBN
    else:
        return True

class IBook(Interface):
    """A book record"""
    title = schema.TextLine(title=u"Title",
                            required=False,
                            default=u'',
                            missing_value=u'')
    isbn = schema.TextLine(title=u"ISBN",
                           required=False,
                           constraint=validateISBN,
                           description=u"ISBN in 10 or 13 digit format",
                           min_length=10,
                           max_length=17 #978-3-540-33807-9
                           )

    creators = schema.Tuple(title=u"Authors",
                            value_type=schema.TextLine(),
                            default=())
    edition = schema.TextLine(title=u"Edition", required=False)
    publisher = schema.TextLine(title=u"Publisher", required=False)
    issued = schema.TextLine(title=u"Issued", required=False)
    # TODO: set a vocabulary for language
    language = schema.TextLine(title=u"Language", required=False)
    
    subjects = schema.Tuple(title=u"Subjects",
                            value_type=schema.TextLine(),
                            default=())
            
    source = schema.TextLine(title=u"Record source",
                             required=False,
                             description=u"Name of the source of this record.")
    source_url = schema.URI(title=u"Source URL",
                            required=False,
                            description=u"URL of the source of this record.")
    source_item_id = schema.TextLine(title=u"Item ID at Source",
                            required=False,
                            description= (u"Product number or other identifier"
                                          u" for this item at source.")
    )

    @invariant
    def titleOrIsbnGiven(book):
        if (not book.title or not book.title.strip()) and (not book.isbn):
            raise Invalid('Either the title or the ISBN must be given.')

        

