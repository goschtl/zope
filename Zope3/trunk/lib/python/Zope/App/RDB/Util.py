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
"""
$Id: Util.py,v 1.4 2002/07/12 21:37:35 srichter Exp $
"""
from Zope.App.RDB.DatabaseException import DatabaseException
from Zope.App.RDB.Row import RowClassFactory
from Zope.App.RDB.ResultSet import ResultSet

def queryForResults(conn, query):
    """Convenience function to quickly execute a query."""
    
    # XXX need to do typing
    cursor = conn.cursor()

    try:
        cursor.execute(query)
    except Exception, error:
        raise DatabaseException(str(error))

    columns = [c[0] for c in cursor.description]

    row_klass = RowClassFactory(columns)
    
    return ResultSet(columns, cursor.fetchall(), row_klass)









