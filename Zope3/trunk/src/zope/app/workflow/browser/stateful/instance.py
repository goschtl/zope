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
"""ProcessInstance views for a stateful workflow
 
$Id: instance.py,v 1.6 2004/03/13 23:55:30 srichter Exp $
"""
from zope.component import getService
from zope.proxy import removeAllProxies
from zope.publisher.browser import BrowserView
from zope.security.proxy import trustedRemoveSecurityProxy
from zope.schema import getFields

from zope.app.browser.form.submit import Update
from zope.app.form.utility import setUpWidget, applyWidgetsChanges
from zope.app.form.interfaces import IInputWidget
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.dublincore.interfaces import IZopeDublinCore
from zope.app.servicenames import Workflows

from zope.app.workflow.interfaces import IProcessInstanceContainer
from zope.app.workflow.interfaces import IProcessInstanceContainerAdaptable

__metaclass__ = type

 
class ManagementView(BrowserView):

    __used_for__ = IProcessInstanceContainerAdaptable

    def __init__(self, context, request):
        super(ManagementView, self).__init__(context, request)
        workflow = self._getSelWorkflow() 
        if workflow.data is None:
            return
        schema = workflow.data.getSchema()
        for name, field in getFields(schema).items():
            # setUpWidget() does not mutate the field, so it is ok.
            field = trustedRemoveSecurityProxy(field)
            setUpWidget(self, name, field, IInputWidget,
                        value=getattr(workflow.data, name))
        
    def _extractContentInfo(self, item):
        id, processInstance = item
        info = {}
        info['id']  = id
        info['name'] = self._getTitle(
            self._getProcessDefinition(processInstance))
        return info

    def listContentInfo(self):
        return map(self._extractContentInfo,
                   IProcessInstanceContainer(self.context).items())

    def getWorkflowTitle(self):
        pi = self._getSelWorkflow()
        if pi is None:
            return None
        
        return self._getTitle(self._getProcessDefinition(pi))

    def getTransitions(self):
        info = {}
        pi   = self._getSelWorkflow()
        if pi is None:
            return info

        pd = self._getProcessDefinition(pi)
        clean_pd = removeAllProxies(pd)

        current_state = clean_pd.getState(pi.status)
        adapter = IZopeDublinCore(current_state)
        info['status'] = adapter.title or pi.status

        transition_names = pi.getOutgoingTransitions()
        trans_info = []
        for name in transition_names:
            transition = clean_pd.getTransition(name)
            adapter = IZopeDublinCore(transition)
            trans_info.append({'name':name,
                               'title': adapter.title or name})
        info['transitions'] = trans_info
        return info

    def fireTransition(self):
        pi    = self._getSelWorkflow()
        if pi is None:
            return

        trans = self.request.get('selTransition', None)
        self.request.response.redirect('@@workflows.html?workflow=%s'
                                       % pi.processDefinitionName)
        if pi and trans:
            pi.fireTransition(trans)


    def _getTitle(self, obj):
        return (IZopeDublinCore(obj).title or obj.__name___)

 
    def _getSelWorkflow(self):
        reqWorkflow = self.request.get('workflow', u'')
        pi_container = IProcessInstanceContainer(self.context)
        if reqWorkflow is u'':
            available_instances = pi_container.keys()
            if len(available_instances) > 0:
                pi = pi_container[available_instances[0]]
            else:
                pi = None
        else:
            pi = pi_container[reqWorkflow]
        
        return pi


    def _getProcessDefinition(self, processInstance):
        ws = getService(self.context, Workflows)
        return ws.getProcessDefinition(processInstance.processDefinitionName)


    def widgets(self):
        if self._getSelWorkflow().data is None:
            return []
        schema = self._getSelWorkflow().data.getSchema()
        return [getattr(self, name+'_widget')
                for name in getFields(schema).keys()]

    
    def update(self):
        status = ''
        workflow = self._getSelWorkflow() 

        if Update in self.request and workflow.data is not None:
            schema = trustedRemoveSecurityProxy(workflow.data.getSchema())
            changed = applyWidgetsChanges(self, schema, target=workflow.data, 
                names=getFields(schema).keys())
            if changed:
                status = _('Updated Workflow Data.')

        return status
