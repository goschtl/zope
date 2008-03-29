from zope import interface
from zope import component

from z3c.indexing.dispatch.interfaces import IDispatcher

import interfaces

class XapianDispatcher(object):
    """Xapian dispatcher."""

    interface.implements(IDispatcher)

    def __init__(self):
        self._connections = set()

    def index(self, obj, attributes=None):
        self._get_connection(obj).add(self._get_document(obj))
        
    def reindex(self, obj, attributes=None):
        self._get_connection(obj).replace(self._get_document(obj))
                
    def unindex(self, obj):
        self._get_connection(obj).delete(self._get_document(obj).id)

    def flush(self):
        for conn in self._connections:
            conn.flush()

        self._connections.clear()

    def _get_document(self, obj):
        return component.getAdapter(obj, interfaces.IDocument, context=obj)
        
    def _get_connection(self, obj):
        conn = component.getUtility(interfaces.IIndexerConnection, context=obj)

        # keep connection to be able to flush it later
        self._connections.add(conn)
        
        return conn
