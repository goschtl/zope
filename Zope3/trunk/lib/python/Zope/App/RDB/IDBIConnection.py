##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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

Revision information:
$Id: IDBIConnection.py,v 1.1 2002/06/24 11:14:17 srichter Exp $
"""

from Interface import Interface

class IDBIConnection(Interface):
    """A DB-API based Interface """
    
    def cursor():
        """Return a new ICursor Object using the connection.
        
        If the database does not provide a direct cursor concept, the module
        will have to emulate cursors using other means to the extent needed by
        this specification.  """

    def commit():
        """Commit any pending transaction to the database. Note that if the
        database supports an auto-commit feature, this must be initially off.
        An interface method may be provided to turn it back on.

        Database modules that do not support transactions should implement
        this method with void functionality.
        """
        
    def rollback():
        """In case a database does provide transactions this method causes the
        database to roll back to the start of any pending transaction. Closing
        a connection without committing the changes first will cause an
        implicit rollback to be performed.  """

    def close():
        """Close the connection now (rather than whenever __del__ is
        called). The connection will be unusable from this point forward; an
        Error (or subclass) exception will be raised if any operation is
        attempted with the connection. The same applies to all cursor objects
        trying to use the connection.  """
