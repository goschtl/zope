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
$Id: ICursor.py,v 1.3 2002/10/18 09:54:22 jim Exp $
"""

from Interface import Interface
from Interface.Attribute import Attribute

class ICursor(Interface):
    """DB API ICursor interface"""

    description = Attribute("""This read-only attribute is a sequence of
        7-item sequences. Each of these sequences contains information
        describing one result column: (name, type_code, display_size,
        internal_size, precision, scale, null_ok). This attribute will be None
        for operations that do not return rows or if the cursor has not had an
        operation invoked via the executeXXX() method yet.

        The type_code can be interpreted by comparing it to the Type Objects
        specified in the section below. """)

    arraysize = Attribute("""This read/write attribute specifies the number of
        rows to fetch at a time with fetchmany(). It defaults to 1 meaning to
        fetch a single row at a time.

        Implementations must observe this value with respect to the
        fetchmany() method, but are free to interact with the database a
        single row at a time. It may also be used in the implementation of
        executemany().
        """)

    def close():
        """Close the cursor now (rather than whenever __del__ is called).  The
        cursor will be unusable from this point forward; an Error (or
        subclass) exception will be raised if any operation is attempted with
        the cursor.
        """

    def execute(operation, parameters=None):
        """Prepare and execute a database operation (query or
        command). Parameters may be provided as sequence or mapping and will
        be bound to variables in the operation. Variables are specified in a
        database-specific notation (see the module's paramstyle attribute for
        details). [5]

        A reference to the operation will be retained by the cursor. If the
        same operation object is passed in again, then the cursor can optimize
        its behavior. This is most effective for algorithms where the same
        operation is used, but different parameters are bound to it (many
        times).

        For maximum efficiency when reusing an operation, it is best to use
        the setinputsizes() method to specify the parameter types and sizes
        ahead of time. It is legal for a parameter to not match the predefined
        information; the implementation should compensate, possibly with a
        loss of efficiency.

        The parameters may also be specified as list of tuples to e.g. insert
        multiple rows in a single operation, but this kind of usage is
        depreciated: executemany() should be used instead.

        Return values are not defined.
        """


    def executemany(operation, seq_of_parameters):
        """Prepare a database operation (query or command) and then execute it
        against all parameter sequences or mappings found in the sequence
        seq_of_parameters.

        Modules are free to implement this method using multiple calls to the
        execute() method or by using array operations to have the database
        process the sequence as a whole in one call.
        
        The same comments as for execute() also apply accordingly to this
        method.

        Return values are not defined. 
        """
        
    def fetchone():
        """Fetch the next row of a query result set, returning a single
        sequence, or None when no more data is available. [6]

        An Error (or subclass) exception is raised if the previous call to
        executeXXX() did not produce any result set or no call was issued yet.
        """

    def fetchmany(size=arraysize):
        """Fetch the next set of rows of a query result, returning a sequence
        of sequences (e.g. a list of tuples). An empty sequence is returned
        when no more rows are available.

        The number of rows to fetch per call is specified by the parameter. If
        it is not given, the cursor's arraysize determines the number of rows
        to be fetched. The method should try to fetch as many rows as
        indicated by the size parameter. If this is not possible due to the
        specified number of rows not being available, fewer rows may be
        returned.

        An Error (or subclass) exception is raised if the previous call to
        executeXXX() did not produce any result set or no call was issued yet.

        Note there are performance considerations involved with the size
        parameter. For optimal performance, it is usually best to use the
        arraysize attribute. If the size parameter is used, then it is best
        for it to retain the same value from one fetchmany() call to the next.
        """

    def fetchall():
        """Fetch all (remaining) rows of a query result, returning them as a
        sequence of sequences (e.g. a list of tuples). Note that the cursor's
        arraysize attribute can affect the performance of this operation.

        An Error (or subclass) exception is raised if the previous call to
        executeXXX() did not produce any result set or no call was issued yet.
        """
        
