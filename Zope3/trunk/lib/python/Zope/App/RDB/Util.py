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
$Id: Util.py,v 1.5 2002/08/08 17:07:03 srichter Exp $
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

    if cursor.description is not None:
        columns = [c[0] for c in cursor.description]
        results = cursor.fetchall()
    else:
        # Handle the case that the query was not a SELECT
        columns = []
        results = []

    row_klass = RowClassFactory(columns)
    
    return ResultSet(columns, results, row_klass)









