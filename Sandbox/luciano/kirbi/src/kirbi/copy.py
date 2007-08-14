import grok
from zope.interface import Interface, implements, invariant
from zope import schema

class ICopy(Interface):
    """An exemplar of a book."""
    
    book_id = schema.TextLine(title=u"Book id",
                    description=u"The id of the book of which this is a copy.",
                    required=True)
    description = schema.Text(title=u"Description",
                    description=(u"Details of this copy, such as autographs,"
                                 u"marks, damage etc."),
                            required=False)
    #XXX: This should be filled automatically.
    catalog_date = schema.Date(title=u"Catalog date",
                    description=u"Date when added to your collection.",
                            required=False)
    
class Copy(grok.Container):
    """An exemplar of a book.
    
    A Copy is associated to a Book instance.
    
    A Copy can contain Lease instances, recording each time it was lent.   
    """

    implements(ICopy)
    
    def __init__(self, book_id):
        super(User, self).__init__()
        

class ILease(Interface):
    """A book lease."""
    
    copy_id = schema.TextLine(title=u"Copy id",
                    description=u"The id of the copy being lent.",
                    required=True)

    # Note: the lender_id can usually be obtained from the copy, however if a
    # copy is given to a new owner, the lease history would become incomplete.
    lender_id = schema.Text(title=u"Lender",
                            description=(u"Lender login."),
                            required=True)

    borrower_id = schema.Text(title=u"Borrower",
                            description=(u"Borrower login."),
                            required=True)

    #XXX: This should be filled automatically.
    request_date = schema.Date(title=u"Request date",
                    description=u"When the lease was requested.",
                    required=False)

    delivery_date = schema.Date(title=u"Delivery date",
                    description=u"When the copy was delivered to the borrower.",
                    required=False)

    due_date = schema.Date(title=u"Due date",
                description=u"When the copy should be returned to the lender.",
                required=False)
                           
    return_date = schema.Date(title=u"Returnd date",
                    description=u"When the copy was returned to the lender.",
                    required=False)

    @invariant
    def dueAfterDelivery(lease):
        if not (lease.due_date > lease.delivery_date):
            raise Invalid(u'The due date must be after the delivery date.')
