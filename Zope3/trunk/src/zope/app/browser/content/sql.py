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
$Id: sql.py,v 1.2 2002/12/25 14:12:30 jim Exp $
"""
from zope.proxy.introspection import removeAllProxies
from zope.publisher.browser import BrowserView
from zope.app.interfaces.content.sql import ISQLScript
from zope.app.interfaces.rdb import DatabaseException

class SQLScriptTest(BrowserView):
    """Edit View for SQL Scripts"""
    __implements__ = BrowserView.__implements__
    __used_for__ = ISQLScript

    error = None

    def getArguments(self):
        form = self.request.form
        arguments = {}
        for arg in self.context.getArguments().items():
            value = form.get(arg[0])
            if value is None:
                value = arg[1].get('default')
            if value is not None:
                arguments[arg[0].encode('UTF-8')] = value
        return arguments

    def getTestResults(self):
        try:
            return self.context(**self.getArguments())
        except DatabaseException, error:
            self.error = error
            return []

    def getFormattedError(self):
        error = str(self.error)
        return error

    def getRenderedSQL(self):
        return self.context.getTemplate()(**self.getArguments())
