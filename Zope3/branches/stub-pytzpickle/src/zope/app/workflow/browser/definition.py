##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""ProcessDefinition registration adding view

$Id$
"""
from zope.app.traversing.api import traverse
from zope.app.component.interfaces.registration import IRegistered
from zope.app.workflow.interfaces import IProcessDefinitionImportHandler
from zope.app.workflow.interfaces import IProcessDefinitionExportHandler


class ProcessDefinitionView(object):

    def getName(self):
        return """I'm a dummy ProcessInstance"""


class ImportExportView(object):

    def importDefinition(self):
        xml = str(self.request.get('definition'))
        if xml:
            IProcessDefinitionImportHandler(self.context).doImport(xml)
        self.request.response.redirect('@@importexport.html?success=1')

    def exportDefinition(self):
        return IProcessDefinitionExportHandler(self.context).doExport()
