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

$Id: __init__.py,v 1.2 2003/02/01 19:19:03 jack-e Exp $
"""

from zope.interface import Interface
from zope.interface import Attribute
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

    def createProcessInstance(definition_name):
        """Create a process instance from a process definition.
        """






class IProcessDefinition(Interface):
    """Interface for workflow process definition.
    """

    name = Attribute("""The name of the ProcessDefinition""")


    def createProcessInstance():
        """Create a new process instance for this process definition.

        Returns an IProcessInstance.
        """



class IProcessDefinitionConfiguration(INamedComponentConfiguration):
    """Configuration for a workflow process definition.
    """





class IProcessInstance(Interface):
    """Workflow process instance.

    Represents the instance of a process defined by a ProcessDefinition.
    """

    status = Attribute("The state in which the workitem is.")

    processDefinition = Attribute("The process definition.")



class IProcessInstanceContainer(Interface):
    """Workflow process instance container.
    """

    def addProcessInstance(name, pi):
        """Add the process instance, associated to name.
        """

    def getProcessInstance(name):
        """Get the process instance associated to the given name.
        """

    def getProcessInstanceNames():
        """Get the names associated to all process instances.
        """

    def delProcessInstance(name):
        """Remove the process instance associated to name.
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



