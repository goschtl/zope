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
    Interfaces for workflow-related events.
"""

from Interface import Interface

class IWorkflowEvent( Interface ):
    """
        Base interface for events related to workflow.
    """

class IWorkflowActionEvent( IWorkflowEvent ):
    """
        Common base for events related to workflow-aware components
        (e.g.  WorkItems, for WfMC-style activity-based workflows,
        or a new content object, for DCWorkflow-style document-based
        workflows).
    """
    def getAction():
        """
            Return the workflow-aware component which the event is
            "about".
        """

class IWorkflowActionCreatedEvent( IWorkflowActionEvent ):
    """
        Note the creation of a new workflow-aware component (a
        WorkItem, for WfMC-style activity-based workflows, or a
        new content object, for DCWorkflow-style document-based
        workflows.
    """

class IWorkflowActionAssignedEvent( IWorkflowActionEvent ):
    """
        Note the assignment of a workflow-aware action.
    """

class IWorkflowActionBegunEvent( IWorkflowActionEvent ):
    """
        Note the beginning of a workflow-aware action.
    """

class IWorkflowActionCompletedEvent(IWorkflowActionEvent):
    """
        Note the completion of a WorkItem or a transition.
    """

class IWorkflowActionSuspendedEvent( IWorkflowActionEvent ):
    """
        Note the suspension of a workflow-aware action.
    """

class IWorkflowActionExceptionEvent(IWorkflowActionEvent):
    """
        Note that the execution of an action had an exceptional termination.
    """
