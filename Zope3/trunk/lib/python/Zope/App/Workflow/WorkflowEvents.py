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
from IWorkflowEvents import IWorkflowActionCreatedEvent
from IWorkflowEvents import IWorkflowActionAssignedEvent
from IWorkflowEvents import IWorkflowActionBegunEvent
from IWorkflowEvents import IWorkflowActionCompletedEvent
from IWorkflowEvents import IWorkflowActionSuspendedEvent
from IWorkflowEvents import IWorkflowActionExceptionEvent


class WorkflowActionEvent:
    """
        Base class for all action-related events.
    """
    def __init__( self, action ):
        self._action = action

    def getAction(self):
        '''See interface IWorkflowActionCreatedEvent'''
        return self._action

class WorkflowActionCreatedEvent( WorkflowActionEvent ):


    __implements__ =  IWorkflowActionCreatedEvent

    ############################################################
    # Implementation methods for interface
    # Zope.App.Workflow.IWorkflowEvents.IWorkflowActionCreatedEvent
    # getAction:  use inherited implementation

    #
    ############################################################


class WorkflowActionAssignedEvent( WorkflowActionEvent ):


    __implements__ =  IWorkflowActionAssignedEvent

    ############################################################
    # Implementation methods for interface
    # Zope.App.Workflow.IWorkflowActionAssignedEvent
    # getAction:  use inherited implementation

    #
    ############################################################


class WorkflowActionBegunEvent( WorkflowActionEvent ):


    __implements__ =  IWorkflowActionBegunEvent

    ############################################################
    # Implementation methods for interface
    # Zope.App.Workflow.IWorkflowActionBegunEvent
    # getAction:  use inherited implementation

    #
    ############################################################


class WorkflowActionCompletedEvent( WorkflowActionEvent ):

    __implements__ =  IWorkflowActionCompletedEvent

    ############################################################
    # Implementation methods for interface
    # Zope.App.Workflow.IWorkflowEvents.IWorkflowActionCompletedEvent
    # getAction:  use inherited implementation

    #
    ############################################################


class WorkflowActionSuspendedEvent( WorkflowActionEvent ):

    __implements__ =  IWorkflowActionSuspendedEvent

    ############################################################
    # Implementation methods for interface
    # Zope.App.Workflow.IWorkflowEvents.IWorkflowActionSuspendedEvent

    #getAction -- use inherited
    #
    ############################################################


class WorkflowActionExceptionEvent( WorkflowActionEvent ):

    __implements__ =  IWorkflowActionExceptionEvent

    ############################################################
    # Implementation methods for interface
    # Zope.App.Workflow.IWorkflowEvents.IWorkflowActionExceptionEvent
    # getAction:  use inherited implementation

    #
    ############################################################
