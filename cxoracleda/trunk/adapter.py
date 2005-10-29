"""cx_Oracle database adapter.
"""
import cx_Oracle            
from zope.app.rdb import ZopeDatabaseAdapter, parseDSN
from datetime import datetime

class UnicodeConverter(object):
    
    def __init__(self,encoding):
        self.encoding=encoding
    def __call__(self,s):
        if s==None: return s
        return s.decode(self.encoding)

def convertDate(d):
    if d==None: return d
    return datetime(d.year,d.month,d.day,d.hour,d.minute,d.second,d.fsecond)

class DatabaseAdapter(ZopeDatabaseAdapter):
    """A cx_Oracle adapter for Zope3"""

    threadsafety = 2
    
    def _connection_factory(self):
        """Create a cx_Oracle DBI connection based on the DSN"""

        conn_info = parseDSN(self.dsn)
        
        if conn_info['host']:
            port = int(conn_info['port'] or 1521)
            dsn = cx_Oracle.makedsn(conn_info['host'],
                                    port,
                                    conn_info['dbname'])
        else:
            dsn = conn_info['dbname']
                                    
        connection = cx_Oracle.connect(
            conn_info['username'],
            conn_info['password'],
            dsn,
            threaded=True)
 
        return connection
        
    def getConverter(self,t):

        if t==cx_Oracle.STRING:
            # TODO: check the encoding from the db
            return UnicodeConverter('latin1')
        elif t==cx_Oracle.Timestamp and t != datetime:
            return convertDate
        return super(DatabaseAdapter,self).getConverter(t)
    
    
    
