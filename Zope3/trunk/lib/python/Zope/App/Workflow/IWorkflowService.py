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
    Interfaces for Workflow Service.
"""

from Interface import Interface


class IWorkflowService( Interface ):
    """
        Interface for workflow service.
    """

    def listEngine():
        """
           Return the list of engine and their interfaces
        """
        pass


    def getEngine(IWorkflowEngine):
        """
           Return a workflow engine giving its interface
        """
        pass


    def addEngine(WorkflowEngine):
        """
           Add a workflow engine
        """

    def removeEngine(WorkflowEngine):
        """
           Remove Workflow engine from the system
        """
        pass


    def listWorkflowEngineActions():
        """
           Return an aggregation of the actions provided
           by the present engines
        """

    
