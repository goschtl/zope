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
"""Message Export/Import View

$Id: exportimport.py,v 1.6 2004/03/06 16:50:15 jim Exp $
"""
from zope.app.browser.services.translation import BaseView
from zope.i18n.interfaces import IMessageExportFilter, IMessageImportFilter


class ExportImport(BaseView):

    def exportMessages(self, domains, languages):
        self.request.response.setHeader('content-type',
                                        'application/x-gettext')
        filter = IMessageExportFilter(self.context)
        return filter.exportMessages(domains, languages)

    def importMessages(self, domains, languages, file):
        filter = IMessageImportFilter(self.context)
        filter.importMessages(domains, languages, file)
        return self.request.response.redirect(self.request.URL[-1])
