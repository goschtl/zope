
from zope.app.interfaces.event import ISubscriber
from zope.interface import Interface

class ICatalogIndexUpdate(ISubscriber):
    "A wrapper around an Index that's in a Catalog"

    def clear():
	"Clear everything from the index"

class ICatalogIndexQuery(Interface):
    "la la la la la"

    def search(term): 
	"do a search"

class ICatalogIndex(ICatalogIndexUpdate, ICatalogIndexQuery): 
    pass

