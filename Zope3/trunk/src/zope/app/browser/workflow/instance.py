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
"""ProcessInstance views
 
$Id: instance.py,v 1.1 2003/05/08 17:27:17 jack-e Exp $
"""
__metaclass__ = type

from zope.schema import getFieldNames
from zope.component import queryView, queryAdapter,  getAdapter
from zope.publisher.browser import BrowserView
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from zope.app.interfaces.workflow import IProcessInstanceContainerAdaptable
from zope.app.interfaces.workflow import IProcessInstanceContainer
from zope.app.interfaces.workflow.stateful import IStatefulProcessInstance

 
class InstanceContainerView(BrowserView):

    __used_for__ = IProcessInstanceContainerAdaptable


    def _extractContentInfo(self, item):
        id, obj = item
        info = {}
        info['id'] = id
        info['object'] = obj

        # XXX need to urlencode the id in this case !!!
        info['url'] = "processinstance.html?pi_name=%s" % id
 
        return info
 
 
    def removeObjects(self, ids):
        """Remove objects specified in a list of object ids"""
        container = getAdapter(self.context, IProcessInstanceContainer)
        for id in ids:
            container.__delitem__(id)
 
        self.request.response.redirect('@@processinstances.html')
 
    def listContentInfo(self):
        return map(self._extractContentInfo,
                   getAdapter(self.context, IProcessInstanceContainer).items())
 
    contents = ViewPageTemplateFile('instancecontainer_main.pt')
    contentsMacros = contents
 
    _index = ViewPageTemplateFile('instancecontainer_index.pt')
 
    def index(self):
        if 'index.html' in self.context:
            self.request.response.redirect('index.html')
            return ''
 
        return self._index()    


    # ProcessInstance Details
    # XXX This is temporary till we find a better name to use
    #     objects that are stored in annotations
    #     Steve suggested a ++annotations++<key> Namespace for that.
    #     we really want to traverse to the instance and display a view

    def _getProcessInstanceData(self, data):
        names = getFieldNames(data.__implements__)
        return dict([(name, getattr(data, name, None),) for name in names ])

    def getProcessInstanceInfo(self, pi_name):
        info = {}
        pi = getAdapter(self.context, IProcessInstanceContainer)[pi_name]
        info['status'] = pi.status
        
        # temporary
        if IStatefulProcessInstance.isImplementedBy(pi):
            info['outgoing_transitions'] = pi.getOutgoingTransitions()

        if pi.data is not None:
            info['data'] = self._getProcessInstanceData(pi.data)
        else:
            info['data'] = None
            
        return info

    def _fireTransition(self, pi_name, id):
        pi = getAdapter(self.context, IProcessInstanceContainer)[pi_name]
        pi.fireTransition(id)


    _instanceindex = ViewPageTemplateFile('instance_index.pt')

    def instanceindex(self):
        """ProcessInstance detail view."""
        request = self.request
        pi_name = request.get('pi_name')
        if pi_name is None:
            request.response.redirect('index.html')
            return ''

        if request.has_key('fire_transition'):
            self._fireTransition(pi_name, request['fire_transition'])
        
        return self._instanceindex()
