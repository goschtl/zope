"""cx_Oracle database adapter.
"""
import cx_Oracle            
from zope.app.rdb import ZopeDatabaseAdapter, parseDSN


class UnicodeConverter(object):
    def __init__(self,encoding):
        self.encoding=encoding
    def __call__(self,s):
        if s==None: return s
        return s.decode(self.encoding)
            
class DatabaseAdapter(ZopeDatabaseAdapter):
    """A cx_Oracle adapter for Zope3"""

    def _connection_factory(self):
        """Create a cx_Oracle DBI connection based on the DSN"""

        conn_info = parseDSN(self.dsn)
        connection = cx_Oracle.connect(
            conn_info['username'],
            conn_info['password'],
            conn_info['dbname'])
 
        return connection
        
    def getConverter(self,t):
        if t==cx_Oracle.STRING:
            # TODO: check the encoding from the db
            return UnicodeConverter('latin1')
        return super(DatabaseAdapter,self).getConverter(t)
    
    
    
