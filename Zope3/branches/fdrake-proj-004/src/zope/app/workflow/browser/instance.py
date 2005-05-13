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
"""ProcessInstance views
 
$Id$
"""
import urllib
from zope.schema import getFieldNames
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from zope.app.workflow.interfaces import IProcessInstanceContainerAdaptable
from zope.app.workflow.interfaces import IProcessInstanceContainer
from zope.app.workflow.stateful.interfaces import IStatefulProcessInstance

class InstanceContainerView(object):

    __used_for__ = IProcessInstanceContainerAdaptable

    def _extractContentInfo(self, item):
        id, obj = item
        info = {}
        info['id'] = id
        info['object'] = obj
        info['url'] = "processinstance.html?pi_name=%s" %urllib.quote_plus(id)
        return info

    def removeObjects(self, ids):
        """Remove objects specified in a list of object ids"""
        container = IProcessInstanceContainer(self.context)
        for id in ids:
            container.__delitem__(id)

        self.request.response.redirect('@@processinstances.html')

    def listContentInfo(self):
        return map(self._extractContentInfo,
                   IProcessInstanceContainer(self.context).items())

    contents = ViewPageTemplateFile('instancecontainer_main.pt')
    contentsMacros = contents

    _index = ViewPageTemplateFile('instancecontainer_index.pt')

    def index(self):
        if 'index.html' in self.context:
            self.request.response.redirect('index.html')
            return ''

        return self._index()


    # ProcessInstance Details

    # TODO:
    # This is temporary till we find a better name to use
    # objects that are stored in annotations
    # Steve suggested a ++annotations++<key> Namespace for that.
    # we really want to traverse to the instance and display a view

    def _getProcessInstanceData(self, data):
        names = []
        for interface in providedBy(data):
            names.append(getFieldNames(interface))
        return dict([(name, getattr(data, name, None),) for name in names])

    def getProcessInstanceInfo(self, pi_name):
        info = {}
        pi = IProcessInstanceContainer(self.context)[pi_name]
        info['status'] = pi.status

        # temporary
        if IStatefulProcessInstance.providedBy(pi):
            info['outgoing_transitions'] = pi.getOutgoingTransitions()

        if pi.data is not None:
            info['data'] = self._getProcessInstanceData(pi.data)
        else:
            info['data'] = None

        return info

    def _fireTransition(self, pi_name, id):
        pi = IProcessInstanceContainer(self.context)[pi_name]
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
