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
import re
from zope.interface import implements
from zope.component import getService, createObject
from zope.app.rdb import queryForResults
from zope.tales.interfaces import ITALESExpression
from zope.tales.expressions import NAME_RE

_interp = re.compile(r'\$(%(n)s)|\${(%(n)s(?:/[^}]*)*)}' % {'n': NAME_RE})

class NoConnectionSpecified(Exception):
    pass

class SQLExpr(object):
    """SQL Expression Handler class"""
    implements(ITALESExpression)

    def __init__(self, name, expr, engine):
        # Completely taken from StringExpr
        self._s = expr
        if '%' in expr:
            expr = expr.replace('%', '%%')
        self._vars = vars = []
        if '$' in expr:
            # Use whatever expr type is registered as "path".
            path_type = engine.getTypes()['path']
            parts = []
            for exp in expr.split('$$'):
                if parts: parts.append('$')
                m = _interp.search(exp)
                while m is not None:
                    parts.append(exp[:m.start()])
                    parts.append('%s')
                    vars.append(path_type(
                        'path', m.group(1) or m.group(2), engine))
                    exp = exp[m.end():]
                    m = _interp.search(exp)
                if '$' in exp:
                    raise CompilerError, (
                        '$ must be doubled or followed by a simple path')
                parts.append(exp)
            expr = ''.join(parts)
        self._expr = expr

    def __call__(self, econtext):
        vvals = []
        for var in self._vars:
            v = var(econtext)
            if isinstance(v, (str, unicode)):
                v = sql_quote(v)
            vvals.append(v)

        if econtext.vars.has_key('sql_conn'):
            # TODO: It is hard-coded that the connection name variable is called
            # 'sql_conn'. We should find a better solution.
            conn_name = econtext.vars['sql_conn']
            connection_service = getService("SQLDatabaseConnections",
                                            econtext.context)
            connection = connection_service.getConnection(conn_name)
        elif econtext.vars.has_key('rdb') and econtext.vars.has_key('dsn'):
            rdb = econtext.vars['rdb']
            dsn = econtext.vars['dsn']
            connection = createObject(None, rdb, dsn)()
        else:
            raise NoConnectionSpecified

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
