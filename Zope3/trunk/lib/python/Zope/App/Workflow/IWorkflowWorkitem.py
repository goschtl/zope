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
Interface for workitems
"""

from Interface import Interface


INIT = 0
BEGUN = 1
COMPLETED = 2
FAILED = 3

class WorkflowWorkitemException(Exception):
    """
    Exception for workitems.
    """

class IWorkflowWorkitem(Interface):
    """
    Base interface for workitems.
    """

    def getProcessInstance():
        """
        Get the process instance this workitem is about.
        Returns a IWorkflowProcessInstance.
        """

    def begin(data):
        """
        Begin work on a workitem.
        Can raise WorkflowWorkitemException.
        """

    def complete(data):
        """
        Complete work on a workitem.
        Can raise WorkflowWorkitemException.
        """

    def fail(data):
        """
        Abort work on a workitem.
        Can raise WorkflowWorkitemException.
        """

    def assign(assignee, data):
        """
        Assign a workitem to a principal.
        assignee implements IPrincipal.
        Can raise WorkflowWorkitemException.
        """

    def getState():
        """
        Get the internal state of the workitem.
        Returns one of INIT, BEGUN, COMPLETED, FAILED.
        """

    def getAssignee():
        """
        Get the assignee.
        Returns a IPrincipal or None.
        """
