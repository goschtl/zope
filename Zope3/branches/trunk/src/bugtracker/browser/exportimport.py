##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""XML Import/Export views

$Id: exportimport.py,v 1.1 2003/07/26 13:40:47 srichter Exp $
"""
from bugtracker.exportimport import XMLExport, XMLImport

class XMLExportImport(object):

    def exportXML(self):
        self.request.response.setHeader('Content-Type', 'text/xml')
        return XMLExport(self.context).getXML()

    def importXML(self, xmlfile):
        XMLImport(self.context).processXML(xmlfile)
        return self.request.response.redirect('.')
