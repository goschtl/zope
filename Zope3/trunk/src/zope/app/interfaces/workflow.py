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

from zope.interface import Interface

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


"""
Interface for workitems
"""

from zope.interface import Interface


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



"""
    Interfaces for Workflow Process Definition.
"""

from zope.interface import Interface

class IWorkflowProcessInstance( Interface ):
    """
        Interface for workflow process definition.
    """


    def getStatus():
        """
           Report the status
        """
        pass


    def setActive():
        """
           Change the status to Active according to the state machine
        """
        pass


    def setCompleted():
        """
           Change the status to Completed according to the state machine
        """
        pass


    def listWorkitems():
        """
           List all contained workitems
        """
        pass


    def listActiveWorkitems():
        """
           List contained Active workitems
        """
        pass


    def listFailedWorkitems():
        """
          List contained Failed workitem
        """
        pass




"""
Interface for Workflow Activity Info
WAI encapsulates what can be done at a given point.
"""

from zope.interface import Interface

class IWorkflowActivityInfo(Interface):
    """
    Base interface for Workflow Activity Info.
    """

    def getId():
        """
        Get the Activity Info id.
        """

    def getTitle():
        """
        Get the Activity Info title.
        """

    def getCategory():
        """
        Get the Activity Info category.
        Returns a string (usually 'workflow').
        """

    def getActionURL():
        """
        Get the Activity Info URL that should be called
        to trigger the action.
        Returns an unencoded URL.
        """

    def getPermissions():
        """
        Get the permissions this Activity Info is protected by.
        Returns a list of IPermission.
        The Activity Info is valid if any permission matches.
        """

    def getRoles():
        """
        Get the roles this Activity Info is protected by.
        Returns a list of IRole.
        The Activity Info is valid if any role matches.
        """

    def getCondition():
        """
        Get the guard this Activity Info is protected by.
        Returns a TALES expression (Interface ? XXX).
        """

    def getSource():
        """
        Get the actual action object this Activity Info is about,
        for instance a workitem (task-based workflow) or a transition
        (content-based workflow).
        """



"""
    Interfaces for Workflow Service.
"""

from zope.interface import Interface


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




from zope.interface import Interface


class IWorkflowEngine(Interface):
    """
    Base interface for workflow engine.
    """

    def getProcessInstance (process_id):
        """
        """

    def listProcessInstances ():
        """
        """

    def getWorklist (user, process_instance = None):
        """
        """


class IOpenflowEngine(IWorkflowEngine):
    """
    Interface for activity-based workflow engine.
    """

    def getProcessDefinition(process_definition_id):
        """
        """
