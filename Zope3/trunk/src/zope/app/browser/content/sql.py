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
$Id: sql.py,v 1.5 2003/02/20 16:46:04 stevea Exp $
"""
from zope.publisher.browser import BrowserView
from zope.app.interfaces.content.sql import ISQLScript
from zope.app.interfaces.rdb import DatabaseException
from zope.proxy.context import ContextMethod

class SQLScriptTest(BrowserView):
    """Edit View for SQL Scripts"""

    # XXX: if the following line is uncommented, @@test.html stops working
    # __implements__ = BrowserView.__implements__
    #
    # Just found the reason: if you specify __implements__ here, it overrides
    # the one defined in zope.app.pagetemplate.simpeviewclass.simple,
    # and IBrowserPublisher disappears from the interface list.  Instead,
    # __implements__ of the newly created class (see SimpleViewClass in the
    # same module) ought to be a union of __implements__ of all the base
    # classes.  Or perhaps it should be done by zope.app.browser.form.editview?

    __used_for__ = ISQLScript

    error = None

    def getArguments(self):
        form = self.request.form
        arguments = {}
        # XXX does anyone know what arg[0] and arg[1] are supposed to be?
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
