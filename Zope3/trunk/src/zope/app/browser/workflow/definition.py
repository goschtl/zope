##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""ProcessDefinition registration adding view
 
$Id: definition.py,v 1.3 2003/08/07 17:41:45 srichter Exp $
"""
__metaclass__ = type
 
from zope.component import getAdapter, getView, getUtility
from zope.app.traversing import traverse
from zope.app.interfaces.services.registration import IRegistered
from zope.app.interfaces.workflow import IProcessDefinitionImportExport


class Registered:
    """View for displaying the registrations for a process definition"""

    def uses(self):
        """Get a sequence of registration summaries"""
        component = self.context
        useconfig = getAdapter(component, IRegistered)
        result = []
        for path in useconfig.usages():
            config = traverse(component, path)
            url = getView(config, 'absolute_url', self.request)
            result.append({'name': config.name,
                           'path': path,
                           'url': url(),
                           'status': config.status,
                           })
        return result


class ProcessDefinitionView:
 
    def getName(self):
        return """I'm a dummy ProcessInstance"""


class ImportExportView:

    def doExport(self):
        return self._getUtil().exportProcessDefinition(self.context,
                                                       self.context)

    def doImport(self, data):
        return self._getUtil().importProcessDefinition(self.context,
                                                       data)
    def _getUtil(self):
        return getUtility(self.context, IProcessDefinitionImportExport)

    def importDefinition(self):
        xml = self.request.get('definition')
        if xml:
            self.doImport(xml)
        self.request.response.redirect('@@importexport.html?success=1')

    def exportDefinition(self):
        return self.doExport()
