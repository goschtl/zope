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
"""SQL Script Views

$Id: sql.py,v 1.11 2003/09/21 17:30:31 jim Exp $
"""
from zope.app.interfaces.content.sql import ISQLScript
from zope.app.interfaces.rdb import DatabaseException

class SQLScriptTest:
    """Test the SQL inside the SQL Script"""

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

    def getFormattedError(self):
        error = str(self.error)
        return error

    def getRenderedSQL(self):
        return self.context.getTemplate()(**self.getArguments())
