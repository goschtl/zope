##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Browser Views for IMessageBoard

$Id$
"""
import os
from zope.proxy import removeAllProxies

from zope.app import zapi
from zope.app.registration.interfaces import ActiveStatus
from zope.app.site.interfaces import ISite
from zope.app.site.service import SiteManager, ServiceRegistration
from zope.app.utility.utility import LocalUtilityService, UtilityRegistration
from zope.app.workflow.interfaces import IProcessDefinitionImportHandler
from zope.app.workflow.interfaces import IProcessInstanceContainer
from zope.app.workflow.stateful.contentworkflow import ContentWorkflowsManager
from zope.app.workflow.stateful.definition import StatefulProcessDefinition
from zope.app.workflow.stateful.interfaces import IContentWorkflowsManager
from zope.app.workflow.stateful.interfaces import IStatefulProcessDefinition

import book.messageboard
from book.messageboard.interfaces import IMessage


class AddMessageBoard(object):
    """Add a message board."""
  
    def createAndAdd(self, data):
        content = super(AddMessageBoard, self).createAndAdd(data)
  
        if self.request.get('workflow'):
            folder = removeAllProxies(zapi.getParent(content))
            if not ISite.providedBy(folder):
                sm = SiteManager(folder)
                folder.setSiteManager(sm)
            default = zapi.traverse(folder.getSiteManager(), 'default')
 
            # Create Local Utility Service
            default['Utilities'] = LocalUtilityService()
            rm = default.getRegistrationManager()
            registration = ServiceRegistration(zapi.servicenames.Utilities,
                                               'Utilities', rm)
            key = rm.addRegistration(registration)
            zapi.traverse(rm, key).status = ActiveStatus

            # Create the process definition
            default['publish-message'] = StatefulProcessDefinition()
            pd_path = zapi.getPath(default['publish-message'])
            registration = UtilityRegistration(
                'publish-message', IStatefulProcessDefinition, pd_path)
            pd_id = rm.addRegistration(registration)
            zapi.traverse(rm, pd_id).status = ActiveStatus

            import_util = IProcessDefinitionImportHandler(
                default['publish-message'])
            
            xml = os.path.join(
                os.path.dirname(book.messageboard.__file__), 'workflow.xml')
                
            import_util.doImport(open(xml, mode='r').read())
  
            # Create Content Workflows Manager
            default['ContentWorkflows'] = ContentWorkflowsManager()
            cm_path = zapi.getPath(default['ContentWorkflows'])
            registration = UtilityRegistration(
                'wfcontentmgr', IContentWorkflowsManager, cm_path)
            cm_id = rm.addRegistration(registration)
            zapi.traverse(rm, cm_id).status = ActiveStatus

            contentmgr = default['ContentWorkflows']
            contentmgr.register(IMessage, 'publish-message')

        return content


class ReviewMessages:
    """Workflow: Review all pending messages"""

    def getPendingMessages(self, pmsg):
        """Get all pending messages recursively."""
        msgs = []
        for name, msg in pmsg.items():
            if IMessage.providedBy(msg):
                if hasMessageStatus(msg, 'pending'):
                    msgs.append(msg)
                msgs += self.getPendingMessages(msg)
        return msgs

    def getPendingMessagesInfo(self):
        """Get all the display info for pending messages"""
        msg_infos = []
        for msg in self.getPendingMessages(self.context):
            info = {}
            info['title'] = msg.title
            info['url'] = zapi.getView(
                msg, 'absolute_url', self.request)() + '/@@workflows.html'
            msg_infos.append(info)
        return msg_infos


def hasMessageStatus(msg, status, workflow='publish-message'):
    """Check whether a particular message matches a given status"""
    adapter = zapi.queryAdapter(msg, IProcessInstanceContainer)
    if adapter:
        # No workflow is defined, so the message is always shown.
        if not adapter.keys():
            return True
        for item in adapter.values():
            if item.processDefinitionName != workflow:
                continue
            if item.status == status:
                return True

    return False
