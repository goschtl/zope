##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Workflow-integration interfaces

$Id: interfaces.py 30893 2005-06-22 22:03:13Z srichter $
"""
__docformat__ = "reStructuredText"

from zope import interface

class IProcessDefinitionRegistry(interface.Interface):
    """Process definition registry."""

    def addProcessDefinition(processDefinition):
        """Add a new process definition.
        the ID will be the processDefinition.id"""

    def getProcessDefinition(id):
        """Returns a definition given its ID.
        
        Raise a KeyError if no process definition is available.
        """

    def getProcessDefinitions():
        """Returns all process definitions."""

    def getProcessDefinitionIDs():
        """Returns all process definition IDs."""
        
    def delProcessDefinition(id):
        """Del a process definition given its ID."""
    
class IExtendedAttribute(interface.Interface):
    """Extended XPDL attributes."""
    
    __name__ = interface.Attribute("Name of the extended attribute")
    value = interface.Attribute("Value of the extended attribute")
    content = interface.Attribute("XML content, long value of the extended attribute")