from zope.interface import Interface

class ICatalogView(Interface):
    "Provides read-only access to Catalog"

    def getSubscribed(): "get current subscription status"

class ICatalogQuery(Interface):
    "Provides Catalog Queries"
    def searchResults(**kw):
	"search on the given indexes"

class ICatalogEdit(Interface):
    "Provides read-write Catalog info"
    def clearIndexes(): 
        "nuke the indexes"
    def updateIndexes(): 
        "reindex all objects"
    def subscribeEvents(update=True): 
	"start receiving events, if update, reindex all existing events"
    def unsubscribeEvents(): 
	"stop receiving events"

class ICatalog(ICatalogView, ICatalogQuery, ICatalogEdit): 
    "a content-space catalog"
    pass
