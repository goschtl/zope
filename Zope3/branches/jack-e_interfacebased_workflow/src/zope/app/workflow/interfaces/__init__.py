##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Interfaces for workflow service, definition and instance.

$Id$
"""
from zope.interface import Interface, Attribute
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.container.interfaces import IContainer


class IWorkflowEvent(Interface):
    """This event describes a generic event that is triggered by the workflow
    mechanism."""


class IProcessDefinition(Interface):
    """Interface for workflow process definition."""

    name = Attribute("""The name of the ProcessDefinition""")

    def createProcessInstance(definition_name):
        """Create a new process instance for this process definition.

        Returns an IProcessInstance."""


class IProcessDefinitionElementContainer(IContainer):
    """Abstract Interface for ProcessDefinitionElementContainers."""

    def getProcessDefinition():
        """Return the ProcessDefinition Object."""



class IPIAdapter(Interface):
    """PI Adapter that does the hard work."""

    status            = Attribute('the current status of the PI')
    processDefinition = Attribute('the ProcessDefinition')

    # specify the methods that are used !!!




class IProcessInstance(Interface):
    """Workflow process instance.

    Represents the instance of a process defined by a ProcessDefinition."""




class IProcessDefinitionImportHandler(Interface):
    """Handler for Import of ProcessDefinitions."""

    def canImport(data):
        """Check if handler can import a processdefinition
           based on the data given."""

    def doImport(data):
        """Create a ProcessDefinition from the data given.

        Returns a ProcessDefinition Instance."""


class IProcessDefinitionExportHandler(Interface):
    """Handler for Export of ProcessDefinitions."""

    def doExport():
        """Export a ProcessDefinition into a specific format.

        Returns the serialized value of the given ProcessDefintion."""
