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

$Id: exportimport.py,v 1.3 2002/12/31 02:51:55 jim Exp $
"""
from zope.component import getAdapter
from zope.i18n.interfaces import IMessageExportFilter, IMessageImportFilter

from zope.app.browser.services.translation.basetranslationserviceview \
     import BaseTranslationServiceView
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


class ExportImport(BaseTranslationServiceView):

    exportImportForm = ViewPageTemplateFile('exportimport.pt')

    def exportMessages(self, domains, languages):
        self.request.response.setHeader('content-type',
                                             'application/x-gettext')
        filter = getAdapter(self.context, IMessageExportFilter)
        return filter.exportMessages(domains, languages)

    def importMessages(self, domains, languages, file):
        filter = getAdapter(self.context, IMessageImportFilter)
        filter.importMessages(domains, languages, file)
        return self.request.response.redirect(self.request.URL[-1])
