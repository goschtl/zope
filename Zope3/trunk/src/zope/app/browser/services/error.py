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
""" Define view component for event service control.

$Id: error.py,v 1.3 2003/03/10 20:30:12 jim Exp $
"""

from zope.publisher.browser import BrowserView
from zope.component.contextdependent import ContextDependent
from zope.app.services.errorr import IErrorReportingService
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope.proxy.introspection import removeAllProxies

class EditErrorLog(BrowserView):
    __used_for__ = IErrorReportingService

    def updateProperties(self, keep_entries, copy_to_zlog=None, ignored_exceptions=None):
        errorLog = self.context
        if copy_to_zlog is None:
            copy_to_zlog = 0
        errorLog.setProperties(keep_entries, copy_to_zlog, ignored_exceptions)
        return self.request.response.redirect('index.html')
