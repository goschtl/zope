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
$Id: TestSQL.py,v 1.1 2002/07/10 23:52:18 srichter Exp $
"""
from Zope.Proxy.ProxyIntrospection import removeAllProxies
from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.App.RDB.IZopeDatabaseAdapter import IZopeDatabaseAdapter
from Zope.App.RDB.Util import queryForResults


class TestSQL(BrowserView):
    
    __used_for__ = IZopeDatabaseAdapter

    def getTestResults(self):
        sql = self.request.form['sql']
        adapter = removeAllProxies(self.context)
        result = queryForResults(adapter(), sql)
        return result
