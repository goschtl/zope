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
$Id: sql.py,v 1.3 2003/01/23 09:46:28 ryzaja Exp $
"""
from zope.publisher.browser import BrowserView
from zope.app.interfaces.content.sql import ISQLScript
from zope.app.interfaces.rdb import DatabaseException
from zope.proxy.context import ContextMethod

class SQLScriptTest(BrowserView):
    """Edit View for SQL Scripts"""

    # XXX: if the following line is uncommented, @@test.html stops working
    # __implements__ = BrowserView.__implements__
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
        self.context.getConnection()
        try:
            return self.context(**self.getArguments())
        except (DatabaseException, AttributeError), error:
            self.error = error
            return []

    getTestResults = ContextMethod(getTestResults)

    def getFormattedError(self):
        error = str(self.error)
        return error

    def getRenderedSQL(self):
        return self.context.getTemplate()(**self.getArguments())
