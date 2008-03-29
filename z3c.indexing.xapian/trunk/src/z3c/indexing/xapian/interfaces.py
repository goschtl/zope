from zope import interface

class IResolver(interface.Interface):
    """An object resolver.

    Xapian identifies searched documents with an identification
    string.
    """

    interface.Attribute(
        """Protocol identifier.""")

    def getId(obj):
        """Return an object identification string."""

    def getObject(id):
        """Return an object given an identification string."""

class IDocument(interface.Interface):
    """A Xapian indexing document."""

    id = interface.Attribute(
        """Document id.""")

class IConnectionHub(interface.Interface):
    """Search connection storage and retrieval.

    Automatic reconnections with connection aging. Connections are all
    thread local.
    """

    def invalidate():
        """Invalidate existing connection."""

    def get():
        """Retrieves a connection."""

class ISearchConnection(interface.Interface):
    """A search connection to Xapian."""

class IIndexerConnection(interface.Interface):
    """An indexer connection to Xapian."""

    def add(document):
        """Adds document to database."""

    def replace(document):
        """Replaces existing document."""

    def delete(document_id):
        """Removed document from database."""
