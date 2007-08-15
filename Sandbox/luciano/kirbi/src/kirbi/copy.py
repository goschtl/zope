import grok
from interfaces import ICopy, ILease
from zope.interface import Interface, implements, invariant
from zope import schema

class Copy(grok.Container):
    """An exemplar of a book.
    
    A copy is associated to a Book instance.
    
    A copy can contain Lease instances, recording each time it was lent.
    When a copy is transferred or deleted, the lease history automatically
    goes with it.
    """

    implements(ICopy)
    
    def __init__(self, book_id):
        super(User, self).__init__()
        
