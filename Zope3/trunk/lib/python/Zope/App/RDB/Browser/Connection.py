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
"""Zope database adapter edit view

$Id: Connection.py,v 1.2 2002/12/12 11:32:34 mgedmin Exp $
"""
from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.App.RDB.IZopeDatabaseAdapter import IZopeDatabaseAdapter

class Connection(BrowserView):

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
