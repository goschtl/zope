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
$Id: sql.py,v 1.9 2003/06/11 13:47:57 srichter Exp $
"""
from zope.publisher.browser import BrowserView
from zope.app.interfaces.content.sql import ISQLScript
from zope.app.interfaces.rdb import DatabaseException
from zope.context import ContextMethod

class SQLScriptTest(BrowserView):
    """Edit View for SQL Scripts"""

    __used_for__ = ISQLScript

    error = None

    def getArguments(self):
        form = self.request.form
        arguments = {}

        for argname, argvalue in self.context.getArguments().items():
            value = form.get(argname)
            if value is None:
                value = argvalue.get('default')
            if value is not None:
                arguments[argname.encode('UTF-8')] = value
        return arguments

    def getTestResults(self):
        try:
            return self.context(**self.getArguments())
        except (DatabaseException, AttributeError, Exception), error:
            self.error = error
            return []

    getTestResults = ContextMethod(getTestResults)

    def getFormattedError(self):
        error = str(self.error)
        return error

    def getRenderedSQL(self):
        return self.context.getTemplate()(**self.getArguments())
