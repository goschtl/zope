##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""
    Interfaces for workflow service, definition and instance.

$Id: __init__.py,v 1.5 2003/02/06 01:03:51 jack-e Exp $
"""

from zope.interface import Interface
from zope.interface import Attribute
from zope.interface.common.mapping \
     import IEnumerableMapping
from zope.app.interfaces.container import IContainer
from zope.app.interfaces.services.configuration \
     import INamedComponentConfiguration




class IWorkflowService(Interface):
    """Workflow service.

    A workflow service manages the process definitions.
    """

    def getProcessDefinitionNames():
        """Return the definition names.

        Returns a sequence of names.
        """

    def getProcessDefinition(name):
        """Return the IProcessDefinition for the name.
        """

    def queryProcessDefinition(name, default=None):
        """Return the IProcessDefinition for the name or default.
        """

    def createProcessInstance(definition_name):
        """Create a process instance from a process definition.
        """



class IProcessDefinitionConfiguration(INamedComponentConfiguration):
    """Configuration for a workflow process definition.
    """






class IProcessDefinition(Interface):
    """Interface for workflow process definition.
    """

    name = Attribute("""The name of the ProcessDefinition""")


    def createProcessInstance():
        """Create a new process instance for this process definition.

        Returns an IProcessInstance.
        """


class IProcessDefinitionElementContainer(IContainer):
    """Abstract Interface for ProcessDefinitionElementContainers.
    """




class IProcessInstance(Interface):
    """Workflow process instance.

    Represents the instance of a process defined by a ProcessDefinition.
    """

    status = Attribute("The status in which the workitem is.")

    processDefinitionName = Attribute("The process definition Name.")





class IProcessInstanceContainer(IContainer):
    """Workflow process instance container.
    """






class IProcessInstanceContainerAdaptable(Interface):
    """Marker interface for components that can be
       adapted to a process instance container.
    """





class IProcessInstanceControl(Interface):
    """Interface to interact with a process instance.
    """

    def start():
        """Start a process instance.
        """

    def finish():
        """Finish a process instance.
        """




class IWorklistHandler(Interface):
    """Base interface for Workflow Worklist Handler.
    """

    def getWorkitems():
        """Return a sequence of workitem.
        """





class IProcessDefinitionImportExport(Interface):
    """ProcessDefinition Import/Export.
    """

    def importProcessDefinition(process_definition):
        """Import a Process Definition
        """

    def exportProcessDefinition(pd_id):
        """Export a Process Definition
        """



