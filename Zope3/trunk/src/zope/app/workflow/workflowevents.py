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
from zope.app.interfaces.workflow import IWorkflowActionCreatedEvent
from zope.app.interfaces.workflow import IWorkflowActionAssignedEvent
from zope.app.interfaces.workflow import IWorkflowActionBegunEvent
from zope.app.interfaces.workflow import IWorkflowActionCompletedEvent
from zope.app.interfaces.workflow import IWorkflowActionSuspendedEvent
from zope.app.interfaces.workflow import IWorkflowActionExceptionEvent


class WorkflowActionEvent:
    """
        Base class for all action-related events.
    """
    def __init__( self, action ):
        self._action = action

    def getAction(self):
        '''See interface IWorkflowActionCreatedEvent'''
        return self._action

class WorkflowActionCreatedEvent(WorkflowActionEvent):


    __implements__ =  IWorkflowActionCreatedEvent


class WorkflowActionAssignedEvent(WorkflowActionEvent):


    __implements__ =  IWorkflowActionAssignedEvent


class WorkflowActionBegunEvent(WorkflowActionEvent):


    __implements__ =  IWorkflowActionBegunEvent


class WorkflowActionCompletedEvent(WorkflowActionEvent):

    __implements__ =  IWorkflowActionCompletedEvent


class WorkflowActionSuspendedEvent(WorkflowActionEvent):

    __implements__ =  IWorkflowActionSuspendedEvent


class WorkflowActionExceptionEvent(WorkflowActionEvent):

    __implements__ =  IWorkflowActionExceptionEvent
