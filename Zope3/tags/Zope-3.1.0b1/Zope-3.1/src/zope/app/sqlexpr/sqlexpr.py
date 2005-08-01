##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""SQL Expression Type

$Id$
"""
from zope.component.exceptions import ComponentLookupError
from zope.interface import implements
from zope.tales.interfaces import ITALESExpression
from zope.tales.expressions import StringExpr
from zope.app import zapi
from zope.app.exception.interfaces import UserError 
from zope.app.rdb import queryForResults
from zope.app.rdb.interfaces import IZopeDatabaseAdapter, IZopeConnection

class ConnectionError(UserError):
    """This exception is raised when the user did not specify an RDB
    connection."""

class SQLExpr(StringExpr):
    """SQL Expression Handler class"""

    def __call__(self, econtext):
        if econtext.vars.has_key('sql_conn'):
            # TODO: It is hard-coded that the connection name variable is called
            # 'sql_conn'. We should find a better solution.
            conn_name = econtext.vars['sql_conn']
            adapter = zapi.queryUtility(IZopeDatabaseAdapter, conn_name)
            if adapter is None:
                raise ConnectionError, \
                      ("The RDB DA name, '%s' you specified is not "
                       "valid." %conn_name)
        elif econtext.vars.has_key('rdb') and econtext.vars.has_key('dsn'):
            rdb = econtext.vars['rdb']
            dsn = econtext.vars['dsn']
            try:
                adapter = zapi.createObject(rdb, dsn)
            except ComponentLookupError:
                raise ConnectionError, \
                      ("The factory id, '%s', you specified in the `rdb` "
                       "attribute did not match any registered factory." %rdb)

            if not IZopeDatabaseAdapter.providedBy(adapter):
                raise ConnectionError, \
                      ("The factory id, '%s', you specifed did not create a "
                       "Zope Database Adapter component." %rdb)
        else:
            raise ConnectionError, \
                  'You did not specify a RDB connection.'

        connection = adapter()
        vvals = []
        for var in self._vars:
            v = var(econtext)
            if isinstance(v, (str, unicode)):
                v = sql_quote(v)
            vvals.append(v)
        query = self._expr % tuple(vvals)
        return queryForResults(connection, query)

    def __str__(self):
        return 'sql expression (%s)' % `self._s`

    def __repr__(self):
        return '<SQLExpr %s>' % `self._s`


def sql_quote(value):
    if value.find("\'") >= 0:
        value = "''".join(value.split("\'"))
    return "%s" %value
