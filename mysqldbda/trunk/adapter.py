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

$Id: Adapter.py,v 1.3 2003/06/05 16:42:31 philikon dead $
"""

import MySQLdb

from zope.app.rdb import ZopeDatabaseAdapter, parseDSN

dsn2option_mapping = {'dbname':'dbname',
                      'port':'port',
                      'host':'host',
                      'username':'user',
                      'password':'passwd'}

class MySQLdbAdapter(ZopeDatabaseAdapter):
    """A MySQLdb adapter for Zope3"""

    def _connection_factory(self):
        """Create a MySQLdb DBI connection based on the DSN"""

        conn_info = parseDSN(self.dsn)
        print '*'*78
        print conn_info
        print '*'*78
        return MySQLdb.Connect(db=conn_info['dbname'],
                               host=conn_info['host'],
                               user=conn_info['username'],
                               passwd=conn_info['password'],
                               port=int(conn_info['port'] or '3306'))
                      
