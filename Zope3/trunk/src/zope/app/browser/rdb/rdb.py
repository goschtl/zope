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

$Id: rdb.py,v 1.1 2003/02/07 15:48:39 jim Exp $
"""
from zope.component import getFactory
from zope.proxy.introspection import removeAllProxies
from zope.publisher.browser import BrowserView

from zope.app.interfaces.container import IAdding
from zope.app.interfaces.rdb import IZopeDatabaseAdapter
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.rdb import queryForResults


class TestSQL(BrowserView):

    __used_for__ = IZopeDatabaseAdapter

    def getTestResults(self):
        sql = self.request.form['sql']
        adapter = removeAllProxies(self.context)
        result = queryForResults(adapter(), sql)
        return result


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


class AdapterAdd(BrowserView):
    """A base class for Zope database adapter adding views.

    Subclasses need to override _adapter_factory_id.
    """

    __used_for__ = IAdding

    # This needs to be overridden by the actual implementation
    _adapter_factory_id = None

    add = ViewPageTemplateFile('rdbadd.pt')

    def action(self, dsn):
        factory = getFactory(self, self._adapter_factory_id)
        adapter = factory(dsn)
        self.context.add(adapter)
        self.request.response.redirect(self.context.nextURL())
