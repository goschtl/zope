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
"""Content Workflows Manager

Associates content objects with some workflow process definitions.

$Id$
"""
from persistent import Persistent
from persistent.dict import PersistentDict

from zope.app import zapi
from zope.app.event.interfaces import IObjectCreatedEvent
from zope.app.servicenames import Utilities

from zope.app.workflow.interfaces import IProcessInstanceContainer
from zope.app.workflow.interfaces import IProcessInstanceContainerAdaptable
from zope.app.workflow.stateful.interfaces import IContentWorkflowsManager
from zope.app.workflow.instance import createProcessInstance
from zope.interface import implements, providedBy
from zope.app.container.contained import Contained


def NewObjectProcessInstanceCreator(obj, event):
    #  used for: IProcessInstanceContainerAdaptable, IObjectCreatedEvent

    pi_container = IProcessInstanceContainer(obj)

    for (ignored, cwf) in zapi.getUtilitiesFor(IContentWorkflowsManager):
        # here we will lookup the configured processdefinitions
        # for the newly created compoent. For every pd_name
        # returned we will create a processinstance.

        # Note that we use getUtilitiesFor rather than getAllUtilitiesFor
        # so that we don't use overridden content-workflow managers.

        for pd_name in cwf.getProcessDefinitionNamesForObject(obj):

            if pd_name in pi_container.keys():
                continue
            try:
                pi = createProcessInstance(cwf, pd_name)
            except KeyError:
                # No registered PD with that name..
                continue
            pi_container[pd_name] = pi
        

class ContentWorkflowsManager(Persistent, Contained):

    implements(IContentWorkflowsManager)

    def __init__(self):
        super(ContentWorkflowsManager, self).__init__()
        self._registry = PersistentDict()

    def getProcessDefinitionNamesForObject(self, object):
        """See interfaces.workflows.stateful.IContentWorkflowsManager"""
        names = ()
        for iface in providedBy(object):
            names += self.getProcessNamesForInterface(iface)
        return names

    def getProcessNamesForInterface(self, iface):
        """See zope.app.workflow.interfacess.stateful.IContentProcessRegistry"""
        return self._registry.get(iface, ())

    def getInterfacesForProcessName(self, name):
        ifaces = []
        for iface, names in self._registry.items():
            if name in names:
                ifaces.append(iface)
        return tuple(ifaces)

    def register(self, iface, name):
        """See zope.app.workflow.interfacess.stateful.IContentProcessRegistry"""
        if iface not in self._registry.keys():
            self._registry[iface] = ()
        self._registry[iface] += (name,)
        
    def unregister(self, iface, name):
        """See zope.app.workflow.interfacess.stateful.IContentProcessRegistry"""
        names = list(self._registry[iface])
        names = filter(lambda n: n != name, names)
        if not names:
            del self._registry[iface]
        else:
            self._registry[iface] = tuple(names)
