##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""MySQL database adapter.

$Id: Adapter.py,v 1.1 2004/10/10 mriya3
"""

from zope.app.rdb import ZopeDatabaseAdapter, parseDSN

import MySQLdb

dsn2option_mapping = {'dbname':'dbname',
                    'port':'port',
                    'host':'host',
                    'username':'user',
                    'password':'passwd'}

class MySQLStringConverter:
    def __init__(self, encoding):
        self.encoding = encoding

    def __call__(self, string):
        if isinstance(string, str):
            return string.decode(self.encoding)
        elif isinstance(string, unicode):
            return string
        else:
            return string
            
            

class MySQLdbAdapter(ZopeDatabaseAdapter):
    """A MySQLdb adapter for Zope3"""
    
    
    """ MySQLdb types codes"""
    __STRINGtypes = (1, 247, 254, 253)
    __BINARYtypes = (252, 251, 250, 249)
    __DATEtypes = (10, 14)
    __DATETIMEtypes = (7, 12)
    __NUMBERtypes = (0, 5, 4, 9, 3, 8, 1, 13)
    __TIMEtypes = (11)
    
    """ Default string converter """
    __stringConverter =  MySQLStringConverter('UTF-8')
    

    def _connection_factory(self):
        """Create a MySQLdb DBI connection based on the DSN"""

        conn_info = parseDSN(self.dsn)

        print '*'*78
        print conn_info
        print '*'*78
        connection = MySQLdb.Connect(db=conn_info['dbname'],
                            host=conn_info['host'],
                            user=conn_info['username'],
                            passwd=conn_info['password'],
                            port=int(conn_info['port'] or '3306'))
 
        self.__stringConverter = MySQLStringConverter(str(connection.character_set_name()))
        return connection
                    
    def getConverter(self, type):
        'See IDBITypeInfo'
        if type in self.__STRINGtypes:
            return self.__stringConverter
        return self.identity
   

    def identity(self, x):
        return x
    
    
