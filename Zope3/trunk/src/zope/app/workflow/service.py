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

$Id: service.py,v 1.16 2004/03/13 23:55:30 srichter Exp $
"""
from persistent import Persistent

from zope.interface import implements
from zope.schema.interfaces import \
     ITokenizedTerm, IVocabulary, IVocabularyTokenized

from zope.app import zapi
from zope.app.container.contained import Contained
from zope.app.site.interfaces import ISimpleService
from zope.app.servicenames import Workflows
from zope.app.workflow.interfaces import IProcessDefinition, IWorkflowService


class ILocalWorkflowService(IWorkflowService):
    """A Local Workflow Service."""


class WorkflowService(Persistent, Contained):
    """Local Workflow Service implementation."""
    implements(ILocalWorkflowService, ISimpleService)

    def getProcessDefinitionNames(self):
        """See zope.app.workflow.interfaces.IWorkflowService"""
        names = {}
        for name, util in zapi.getUtilitiesFor(self, IProcessDefinition):
            names[name] = None
        return names.keys()

    def getProcessDefinition(self, name):
        """See zope.app.workflow.interfaces.IWorkflowService"""
        return zapi.getUtility(self, IProcessDefinition, name)

    def queryProcessDefinition(self, name, default=None):
        """See zope.app.workflow.interfaces.IWorkflowService"""
        return zapi.queryUtility(self, IProcessDefinition, default, name)

    def createProcessInstance(self, name):
        """See zope.app.workflow.interfaces.IWorkflowService"""
        pd = self.getProcessDefinition(name)
        return pd.createProcessInstance(name)


class ProcessDefinitionTerm:
    """A term representing the name of a process definition."""
    implements(ITokenizedTerm)

    def __init__(self, name):
        self.value = self.token = name


class ProcessDefinitionVocabulary:
    """Vocabulary providing available process definition names."""
    implements(IVocabulary, IVocabularyTokenized)

    def __init__(self, context):
        self.workflows = zapi.getService(context, Workflows)

    def __contains__(self, value):
        """See zope.schema.interfaces.IVocabulary"""
        return value in self.workflows.getProcessDefinitionNames()

    def __iter__(self):
        """See zope.schema.interfaces.IVocabulary"""
        terms = map(lambda p: ProcessDefinitionTerm(p),
                    self.workflows.getProcessDefinitionNames())
        return iter(terms)

    def __len__(self):
        """See zope.schema.interfaces.IVocabulary"""
        return len(self.workflows.getProcessDefinitionNames())

    def getQuery(self):
        """See zope.schema.interfaces.IVocabulary"""
        return None

    def getTerm(self, value):
        """See zope.schema.interfaces.IVocabulary"""
        return ProcessDefinitionTerm(value)

    def getTermByToken(self, token):
        """See zope.schema.interfaces.IVocabularyTokenized"""
        return self.getTerm(token)
