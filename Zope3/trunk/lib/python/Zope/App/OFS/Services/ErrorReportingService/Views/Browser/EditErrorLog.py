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

$Id: EditErrorLog.py,v 1.2 2002/10/23 16:00:19 jim Exp $
"""

from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.ComponentArchitecture.ContextDependent import ContextDependent
from Zope.App.OFS.Services.ErrorReportingService.ErrorReportingService import IErrorReportingService
from Zope.PageTemplate.PageTemplateFile import PageTemplateFile
from Zope.Proxy.ProxyIntrospection import removeAllProxies

class EditErrorLog(BrowserView):
    __used_for__ = IErrorReportingService

    def updateProperties(self, keep_entries, copy_to_zlog=None, ignored_exceptions=None):
        errorLog = self.context
        if copy_to_zlog is None:
            copy_to_zlog = 0
        errorLog.setProperties(keep_entries, copy_to_zlog, ignored_exceptions)
        return self.request.response.redirect('main.html')
 
