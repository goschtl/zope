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
$Id: service.py,v 1.1 2003/05/08 17:27:18 jack-e Exp $
"""
__metaclass__ = type

from persistence import Persistent

from zope.proxy.context import ContextMethod, ContextWrapper

from zope.component import getAdapter
from zope.app.component.nextservice import queryNextService
from zope.app.interfaces.services.configuration \
        import INameComponentConfigurable
from zope.app.services.configuration import NameComponentConfigurable

from zope.app.services.configuration import NamedComponentConfiguration
from zope.app.services.configuration import ConfigurationStatusProperty
from zope.app.interfaces.services.configuration import IUseConfiguration
from zope.app.traversing import traverse, getPath

from zope.app.interfaces.services.service import ISimpleService
from zope.app.interfaces.workflow import IProcessDefinitionConfiguration
from zope.app.interfaces.workflow import IProcessDefinition
from zope.app.interfaces.workflow import IWorkflowService


class ILocalWorkflowService(IWorkflowService, INameComponentConfigurable):
    """A Local WorkflowService.
    """


class WorkflowService(Persistent, NameComponentConfigurable):

    __doc__ = IWorkflowService.__doc__

    __implements__ = ILocalWorkflowService, ISimpleService 
                     

    ############################################################
    # Implementation methods for interface
    # zope.app.interfaces.workflow.IWorkflowService

    def getProcessDefinitionNames(self):
        'See IWorkflowService'
        definition_names = {}
        for name in self.listConfigurationNames():
            registry = self.queryConfigurations(name)
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




class ProcessDefinitionConfiguration(NamedComponentConfiguration):

    __doc__ = IProcessDefinitionConfiguration.__doc__

    __implements__ = (IProcessDefinitionConfiguration,
                      NamedComponentConfiguration.__implements__)

    status = ConfigurationStatusProperty('Workflows')


    def getInterface(self):
        return IProcessDefinition

    # The following hooks are called only if we implement
    # IAddNotifiable and IDeleteNotifiable.

    def afterAddHook(self, configuration, container):
        """Hook method will call after an object is added to container.

        Defined in IAddNotifiable.
        """
        super(ProcessDefinitionConfiguration, self).afterAddHook(configuration,
                                                                 container)
        pd = configuration.getComponent()
        adapter = getAdapter(pd, IUseConfiguration)
        adapter.addUsage(getPath(configuration))


    def beforeDeleteHook(self, configuration, container):
        """Hook method will call before object is removed from container.

        Defined in IDeleteNotifiable.
        """
        pd = configuration.getComponent()
        adapter = getAdapter(pd, IUseConfiguration)
        adapter.removeUsage(getPath(configuration))
        super(ProcessDefinitionConfiguration, self).beforeDeleteHook(configuration,
                                                                     container)
