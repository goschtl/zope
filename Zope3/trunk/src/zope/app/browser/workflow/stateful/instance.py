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
 
$Id: instance.py,v 1.1 2003/05/08 17:27:17 jack-e Exp $
"""
__metaclass__ = type

from zope.schema import getFieldNames
from zope.component import queryView, queryAdapter, getAdapter, getService
from zope.app.services.servicenames import Workflows
from zope.publisher.browser import BrowserView
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from zope.app.interfaces.workflow import IProcessInstanceContainerAdaptable
from zope.app.interfaces.workflow import IProcessInstanceContainer
from zope.app.interfaces.workflow.stateful import IStatefulProcessInstance
from zope.app.interfaces.dublincore import IZopeDublinCore
from zope.proxy.introspection import removeAllProxies
from zope.proxy.context import getWrapperData
 
class ManagementView(BrowserView):

    __used_for__ = IProcessInstanceContainerAdaptable

    def _extractContentInfo(self, item):
        id, processInstance = item
        info = {}
        info['id']  = id
        info['name']=self._getTitle(self._getProcessDefinition(processInstance))
        return info

    def listContentInfo(self):
        return map(self._extractContentInfo,
                   getAdapter(self.context, IProcessInstanceContainer).items())

    contents = ViewPageTemplateFile('instance_manage.pt')
    contentsMacros = contents

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
        adapter = getAdapter(current_state, IZopeDublinCore)
        info['status'] = adapter.title or pi.status

        transition_names = pi.getOutgoingTransitions()
        trans_info = []
        for name in transition_names:
            transition = clean_pd.getTransition(name)
            adapter = getAdapter(transition, IZopeDublinCore)
            trans_info.append({'name':name,
                               'title': adapter.title or name})
        info['transitions'] = trans_info
        return info

    def fireTransition(self):
        pi    = self._getSelWorkflow()
        if pi is None:
            return

        trans = self.request.get('selTransition', None)
        self.request.response.redirect('@@workflows.html?workflow=%s' % pi.processDefinitionName)
        if pi and trans:
            pi.fireTransition(trans)


    def _getTitle(self, obj):
        return getAdapter(obj, IZopeDublinCore).title or getWrapperData(obj)['name']

 
    def _getSelWorkflow(self):
        reqWorkflow = self.request.get('workflow', u'')
        pi_container = getAdapter(self.context, IProcessInstanceContainer)
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


