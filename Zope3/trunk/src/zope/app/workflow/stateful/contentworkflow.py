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
"""Content Workflows Utility

Associates content objects with some workflow process definitions.

$Id: contentworkflow.py,v 1.1 2003/05/08 17:27:19 jack-e Exp $
"""
__metaclass__ = type

from zope.interface import Interface
from persistence import Persistent
from zope.component import getService, queryAdapter
from zope.component.exceptions import ComponentLookupError
from zope.proxy.context import ContextMethod
from zope.proxy.introspection import removeAllProxies

from zope.app.interfaces.event import ISubscriber
from zope.app.interfaces.event import IObjectCreatedEvent
from zope.app.services.servicenames import EventSubscription, Workflows

from zope.app.interfaces.workflow import IProcessInstanceContainer
from zope.app.interfaces.workflow import IProcessInstanceContainerAdaptable
from zope.app.interfaces.workflow.stateful import IContentWorkflowsUtility



class ContentWorkflowsUtility(Persistent):

    __implements__ = IContentWorkflowsUtility, ISubscriber

    def __init__(self):
        super(ContentWorkflowsUtility, self).__init__()
        self._names = ('default',) # _names should be a TypeRegistry

    # ISubscriber

    def notify(self, event):
        """An event occured. Perhaps register this object with the hub."""
        obj = event.object

        # XXX Do i need to removeAllProxies somewhere in here ???
        
        # check if it implements IProcessInstanceContainerAdaptable
        if not IProcessInstanceContainerAdaptable.isImplementedBy(obj):
            return
        
        pi_container = queryAdapter(obj, IProcessInstanceContainer)
        # probably need to adapt to IZopeContainer to use pi_container with
        # context.
        if pi_container is None:
            # Object can't have associated PIs.
            return
        
        if IObjectCreatedEvent.isImplementedBy(event):
            wfs = getService(self, Workflows)

            # here we will lookup the configured processdefinitions
            # for the newly created compoent. For every pd_name
            # returned we will create a processinstance.
            for pd_name in self._names:
                
                if pd_name in pi_container.keys():
                    continue
                try:
                    pi = wfs.createProcessInstance(pd_name)
                    print "CREATED PROCESSINSTANCE:", str(pi)
                except KeyError:
                    # No registered PD with that name..
                    continue
                pi_container.setObject(pd_name, pi)
                
    notify = ContextMethod(notify)

    # IContentWorkflowsUtility

    # control

    currentlySubscribed = False # Default subscription state

    def subscribe(self):
        if self.currentlySubscribed:
            raise ValueError, "already subscribed; please unsubscribe first"
        channel = self._getChannel(None)
        channel.subscribe(self, IObjectCreatedEvent)
        self.currentlySubscribed = True
    subscribe = ContextMethod(subscribe)

    def unsubscribe(self):
        if not self.currentlySubscribed:
            raise ValueError, "not subscribed; please subscribe first"
        channel = self._getChannel(None)
        channel.unsubscribe(self, IObjectCreatedEvent)
        self.currentlySubscribed = False
    unsubscribe = ContextMethod(unsubscribe)

    def isSubscribed(self):
        return self.currentlySubscribed

    def _getChannel(self, channel):
        if channel is None:
            channel = getService(self, EventSubscription)
        return channel
    _getChannel = ContextMethod(_getChannel)

    # config

    def getProcessDefinitionNames(self):
        """Get the process definition names."""
        return self._names

    def setProcessDefinitionNames(self, names):
        """Set the process definition names."""
        self._names = tuple(names)

