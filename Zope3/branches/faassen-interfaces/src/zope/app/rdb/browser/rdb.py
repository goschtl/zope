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
"""Zope database adapter views

$Id: rdb.py,v 1.1 2004/03/02 13:48:28 philikon Exp $
"""
from zope.proxy import removeAllProxies

from zope.app.rdb.interfaces import IZopeDatabaseAdapter
from zope.app.rdb import queryForResults

class TestSQL:

    __used_for__ = IZopeDatabaseAdapter

    def getTestResults(self):
        sql = self.request.form['sql']
        adapter = removeAllProxies(self.context)
        result = queryForResults(adapter(), sql)
        return result


class Connection:
    __used_for__ = IZopeDatabaseAdapter

    def edit(self, dsn):
        self.context.setDSN(dsn)
        return self.request.response.redirect(self.request.URL[-1])

    def connect(self):
        self.context.connect()
        return self.request.response.redirect(self.request.URL[-1])

    def disconnect(self):
        self.context.disconnect()
        return self.request.response.redirect(self.request.URL[-1])
