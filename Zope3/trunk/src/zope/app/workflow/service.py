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
"""Workflow service implementation.

Revision information:
$Id: service.py,v 1.8 2003/06/23 00:31:32 jim Exp $
"""
__metaclass__ = type

from persistence import Persistent
from zope.app.component.nextservice import queryNextService
from zope.app.context import ContextWrapper
from zope.app.interfaces.services.registration import INameComponentRegistry
from zope.app.interfaces.services.registration import IRegistered
from zope.app.interfaces.services.service import ISimpleService
from zope.app.interfaces.workflow import IProcessDefinition
from zope.app.interfaces.workflow import IProcessDefinitionRegistration
from zope.app.interfaces.workflow import IWorkflowService
from zope.app.services.registration import NameComponentRegistry
from zope.app.services.registration import NamedComponentRegistration
from zope.app.traversing import getPath
from zope.component import getAdapter
from zope.context import ContextMethod
from zope.interface import implements


class ILocalWorkflowService(IWorkflowService, INameComponentRegistry):
    """A Local WorkflowService.
    """


class WorkflowService(Persistent, NameComponentRegistry):

    __doc__ = IWorkflowService.__doc__

    implements(ILocalWorkflowService, ISimpleService)

    ############################################################
    # Implementation methods for interface
    # zope.app.interfaces.workflow.IWorkflowService

    def getProcessDefinitionNames(self):
        'See IWorkflowService'
        definition_names = {}
        for name in self.listRegistrationNames():
            registry = self.queryRegistrations(name)
            if registry.active() is not None:
                definition_names[name] = 0
        service = queryNextService(self, "Workflows")
        if service is not None:
            for name in service.getProcessDefinitionNames():
                definition_names[name] = 0
        return definition_names.keys()

    getProcessDefinitionNames = ContextMethod(getProcessDefinitionNames)


    def getProcessDefinition(self, name):
        'See IWorkflowService'
        pd = self.queryActiveComponent(name)
        if pd is not None:
            return ContextWrapper(pd, self, name=name)
        service = queryNextService(self, "Workflows")
        if service is not None:
            return service.getProcessDefinition(name)
        raise KeyError, name

    getProcessDefinition = ContextMethod(getProcessDefinition)


    def queryProcessDefinition(self, name, default=None):
        'See IWorkflowService'
        try:
            return self.getProcessDefinition(name)
        except KeyError:
            return default

    queryProcessDefinition = ContextMethod(queryProcessDefinition)


    def createProcessInstance(self, definition_name):
        pd = self.getProcessDefinition(definition_name)
        return pd.createProcessInstance(definition_name)

    createProcessInstance = ContextMethod(createProcessInstance)

    #
    ############################################################


class ProcessDefinitionRegistration(NamedComponentRegistration):

    __doc__ = IProcessDefinitionRegistration.__doc__

    implements(IProcessDefinitionRegistration)

    serviceType = 'Workflows'

    def getInterface(self):
        return IProcessDefinition

    # The following hooks are called only if we implement
    # IAddNotifiable and IDeleteNotifiable.

    def afterAddHook(self, registration, container):
        """Hook method will call after an object is added to container.

        Defined in IAddNotifiable.
        """
        super(ProcessDefinitionRegistration, self).afterAddHook(registration,
                                                                 container)
        pd = registration.getComponent()
        adapter = getAdapter(pd, IRegistered)
        adapter.addUsage(getPath(registration))


    def beforeDeleteHook(self, registration, container):
        """Hook method will call before object is removed from container.

        Defined in IDeleteNotifiable.
        """
        pd = registration.getComponent()
        adapter = getAdapter(pd, IRegistered)
        adapter.removeUsage(getPath(registration))
        super(ProcessDefinitionRegistration, self).beforeDeleteHook(
            registration, container)
