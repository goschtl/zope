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
$Id: service.py,v 1.11 2003/10/29 20:28:50 sidnei Exp $
"""
__metaclass__ = type

from persistence import Persistent
from zope.component import getService
from zope.app.component.nextservice import queryNextService
from zope.app.interfaces.services.registration import INameComponentRegistry
from zope.app.interfaces.services.registration import IRegistered
from zope.app.interfaces.services.service import ISimpleService
from zope.app.interfaces.workflow import IProcessDefinition
from zope.app.interfaces.workflow import IProcessDefinitionRegistration
from zope.app.interfaces.workflow import IWorkflowService
from zope.app.services.registration import NameComponentRegistry
from zope.app.services.registration import NamedComponentRegistration
from zope.app.services.servicenames import Workflows
from zope.app.traversing import getPath
from zope.component import getAdapter
from zope.app.container.contained import Contained
from zope.interface import implements
from zope.schema.interfaces import \
     ITokenizedTerm, IVocabulary, IVocabularyTokenized


class ILocalWorkflowService(IWorkflowService, INameComponentRegistry):
    """A Local WorkflowService.
    """


class WorkflowService(Persistent, NameComponentRegistry, Contained):

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
        service = queryNextService(self, Workflows)
        if service is not None:
            for name in service.getProcessDefinitionNames():
                definition_names[name] = 0
        return definition_names.keys()




    def getProcessDefinition(self, name):
        'See IWorkflowService'
        pd = self.queryActiveComponent(name)
        if pd is not None:
            return pd
        service = queryNextService(self, Workflows)
        if service is not None:
            return service.getProcessDefinition(name)
        raise KeyError, name



    def queryProcessDefinition(self, name, default=None):
        'See IWorkflowService'
        try:
            return self.getProcessDefinition(name)
        except KeyError:
            return default



    def createProcessInstance(self, definition_name):
        pd = self.getProcessDefinition(definition_name)
        return pd.createProcessInstance(definition_name)


    #
    ############################################################


class ProcessDefinitionRegistration(NamedComponentRegistration):

    __doc__ = IProcessDefinitionRegistration.__doc__

    implements(IProcessDefinitionRegistration)

    serviceType = Workflows

    def getInterface(self):
        return IProcessDefinition

    # The following hooks are called only if we implement
    # IAddNotifiable and IRemoveNotifiable.

    def addNotify(self, event):
        """Hook method will call after an object is added to container.

        Defined in IAddNotifiable.
        """
        super(ProcessDefinitionRegistration, self).addNotify(event)
        pd = self.getComponent()
        adapter = getAdapter(pd, IRegistered)
        adapter.addUsage(getPath(self))


    def removeNotify(self, event):
        """Hook method will call before object is removed from container.

        Defined in IRemoveNotifiable.
        """
        pd = self.getComponent()
        adapter = getAdapter(pd, IRegistered)
        adapter.removeUsage(getPath(self))
        super(ProcessDefinitionRegistration, self).removeNotify(event)


class ProcessDefinitionTerm:

    implements(ITokenizedTerm)

    def __init__(self, name):
        self.value = name
        self.token = name


class ProcessDefinitionVocabulary(object):

    implements(IVocabulary, IVocabularyTokenized)

    def __init__(self, context):
        self.workflows = getService(context, Workflows)

    def __contains__(self, value):
        return value in self.workflows.getProcessDefinitionNames()

    def __iter__(self):
        terms = map(lambda p: ProcessDefinitionTerm(p),
                    self.workflows.getProcessDefinitionNames())
        return iter(terms)

    def __len__(self):
        return len(self.workflows.getProcessDefinitionNames())

    def getQuery(self):
        return None

    def getTerm(self, value):
        return ProcessDefinitionTerm(value)

    def getTermByToken(self, token):
        return self.getTerm(token)
