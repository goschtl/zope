import interfaces
from zope import interface
from zope import component
from zope.schema.fieldproperty import FieldProperty
from ZODB.interfaces import IDatabase
import persistent
import transaction

class DBRoot(persistent.Persistent):

    interface.implements(interfaces.IDBRoot)

    dbName = FieldProperty(interfaces.IDBRoot['dbName'])

    def __init__(self, dbName=None):
        if dbName is not None:
            self.dbName = dbName

    @property
    def _conn(self):
        if self._p_jar is None:
            # get the connection from the resources of the current
            # thransaction
            # XXX can we get the connection in another way
            conn = transaction.get()._resources[0].get_connection(
                self.dbName)
        else:
            conn = self._p_jar
        return conn.get_connection(self.dbName)
        
    
    @property
    def _data(self):
        root = self._conn.root()
        return root
        
    def keys(self):
        '''See interface `IReadContainer`'''
        return self._data.keys()

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, key):
        '''See interface `IReadContainer`'''
        return self._data[key]

    def get(self, key, default=None):
        '''See interface `IReadContainer`'''
        return self._data.get(key, default)

    def values(self):
        '''See interface `IReadContainer`'''
        return self._data.values()

    def __len__(self):
        '''See interface `IReadContainer`'''
        return len(self._data)

    def items(self):
        '''See interface `IReadContainer`'''
        return self._data.items()

    def __contains__(self, key):
        '''See interface `IReadContainer`'''
        return self._data.has_key(key)

    has_key = __contains__

    def __setitem__(self, key, object):
        '''See interface `IWriteContainer`'''
        self._data.__setitem__(key, object)

    def __delitem__(self, key):
        '''See interface `IWriteContainer`'''
        del self._data[key]
