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

$Id: __init__.py,v 1.13 2003/04/09 18:34:29 jack-e Exp $
"""

from zope.interface import Interface
from zope.interface import Attribute
from zope.interface.common.mapping import IEnumerableMapping
from zope.app.interfaces.container import IContainer
from zope.app.interfaces.services.configuration \
     import INamedComponentConfiguration
from zope.app.interfaces.services.configuration import ComponentPath



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

    componentPath = ComponentPath(
        title=u"Component path",
        description=u"The physical path to the component",
        required=True,
        readonly=True,
        )





class IProcessDefinition(Interface):
    """Interface for workflow process definition.
    """

    name = Attribute("""The name of the ProcessDefinition""")

    def createProcessInstance(definition_name):
        """Create a new process instance for this process definition.

        Returns an IProcessInstance.
        """


class IProcessDefinitionElementContainer(IContainer):
    """Abstract Interface for ProcessDefinitionElementContainers.
    """


    def getProcessDefinition():
        """Return the ProcessDefinition Object.
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

    def importProcessDefinition(context, data):
        """Import a Process Definition
        """

    def exportProcessDefinition(context, process_definition):
        """Export a Process Definition
        """



class IGlobalProcessDefinitionImportExport(IProcessDefinitionImportExport):
    """ Global ImportExport with additional method
        to register import/export handlers.
    """

    def addImportHandler(interface, factory):
        """add a factory for an import handler for a certain interface.
        """

    def addExportHandler(interface, factory):
        """add a factory for an export handler for a certain interface.
        """


class IProcessDefinitionImportHandler(Interface):
    """Handler for Import of ProcessDefinitions.
    """
    
    def canImport(context, data):
        """check if handler can import a processdefinition
           based on the data given.
        """

    def doImport(context, data):
        """create a ProcessDefinition from the data given.

        returns a ProcessDefinition Instance.
        """

class IProcessDefinitionExportHandler(Interface):
    """Handler for Export of ProcessDefinitions.
    """

    def doExport(context, process_definition):
        """export a ProcessDefinition into a specific format.

        returns the serialized value of the given ProcessDefintion.
        """
