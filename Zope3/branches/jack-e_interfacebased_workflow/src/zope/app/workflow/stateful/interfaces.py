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
"""Interfaces for stateful workflow process definition.

$Id$
"""
import zope.schema
from zope.security.checker import CheckerPublic

from zope.interface import Interface, Attribute
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ContainerTypesConstraint
from zope.app.container.constraints import ItemTypePrecondition

from zope.app.event.interfaces import IObjectEvent

from zope.app.workflow.interfaces import IWorkflowEvent
from zope.app.workflow.interfaces import IProcessDefinition
from zope.app.workflow.interfaces import IProcessInstance, IPIAdapter
from zope.app.workflow.interfaces import IProcessDefinitionElementContainer

AUTOMATIC = u'Automatic'
MANUAL = u'Manual'
INITIAL = u'INITIAL'

class ITransitionEvent(IWorkflowEvent):
    """An event that signalizes a transition from one state to another."""

    object = Attribute("""The content object whose status will be changed.""")

    process = Attribute("""The process instance that is doing the
                           transition. Note that this object really represents
                           the workflow.""")

    transition = Attribute("""The transition that is being fired/executed. It
                              contains all the specific information, such as
                              source and destination state.""")

class IBeforeTransitionEvent(ITransitionEvent):
    """This event is published before a the specified transition occurs. This
    allows other objects to veto the transition."""

class IAfterTransitionEvent(ITransitionEvent):
    """This event is published after the transition. This is important for
    objects that might change permissions when changing the status."""

class IState(Interface):
    """Interface for state of a stateful workflow process definition."""
    # TODO: Should at least have a title, if not a value as well

    targetInterface = zope.schema.Choice(
        title=_(u"State Interface"),
        description=_(u"An Interface that is used to mark Instances "
                      u"representing that it is in this state."),
        vocabulary="Interfaces",
        default=None,
        required=False)

    #
    # Permissions / Roles
    #

    #permissionRoles = zope.schema.Dict(
    #    title=_(u"Permission Roles mapping"),
    #    description=_(u"This is the permission roles mapping"
    #                  u"this given state."),
    #    required=False)

    #
    # API for permissions / roles
    # DCWorkflow style
    #

    def getProcessDefinitionPermissions(self):
        """Returns the list of permissions defined on the process
        definition
        """

    def getPermissionInfo(p):
        """Get the  permission info from the mapping defined on the state
        """

    def getPermissionRolesMapping():
        """Return the permissions role mapping
        """

    def setPermissionsRolesMapping(mapping):
        """Set the permissions roles mapping
        """

    def getRelevantRoles():
        """returns all the roles subscribed in z3
        """

class IStatefulStatesContainer(IProcessDefinitionElementContainer):
    """Container that stores States."""

    def __setitem__(name, object):
        """Add a state"""

    __setitem__.precondition = ItemTypePrecondition(IState)

class IStateContained(IContained):
    """Interface for state of a stateful workflow process definition."""

    __parent__ = zope.schema.Field(
             constraint = ContainerTypesConstraint(IStatefulStatesContainer))

class ITransition(Interface):
    """Stateful workflow transition."""

    sourceState = zope.schema.Choice(
        title=_(u"Source State"),
        description=_(u"Name of the source state."),
        vocabulary=u"Workflow State Names",
        required=True)

    destinationState = zope.schema.Choice(
        title=_(u"Destination State"),
        description=_(u"Name of the destination state."),
        vocabulary=u"Workflow State Names",
        required=True)

    condition = zope.schema.TextLine(
        title=_(u"Condition"),
        description=_(u"""The condition that is evaluated to decide if the
                        transition can be fired or not."""),
        required=False)

    script = zope.schema.TextLine(
        title=_(u"Script"),
        description=_(u"""The script that is evaluated to decide if the
                        transition can be fired or not."""),
        required=False)

    permission = zope.schema.Choice(
        title=_(u"The permission needed to fire the Transition."),
        vocabulary="Permission Ids",
        default=CheckerPublic,
        required=True)

    triggerMode = zope.schema.Choice(
        title=_(u"Trigger Mode"),
        description=_(u"How the Transition is triggered (Automatic/Manual)"),
        default=MANUAL,
        values=[MANUAL, AUTOMATIC])

    def getProcessDefinition():
        """Return the ProcessDefinition Object."""

class IStatefulTransitionsContainer(IProcessDefinitionElementContainer):
    """Container that stores Transitions."""

    def __setitem__(name, object):
        """Add a transition"""

    __setitem__.precondition = ItemTypePrecondition(ITransition)

class ITransitionContained(IContained):
    """Stateful workflow transition that lives in a
    StatefulTansitionsContainer."""

    __parent__ = zope.schema.Field(
        constraint = ContainerTypesConstraint(IStatefulTransitionsContainer))

class IStatefulProcessDefinition(IProcessDefinition):
    """Interface for stateful workflow process definition."""

    targetInterface = zope.schema.Choice(
        title=_(u"Process Interface"),
        description=_(u"Interface that represents the Process and "
                      u"is extended by this Process's States."),
        vocabulary="Interfaces",
        default=None,
        required=False)

    states = Attribute("State objects container.")

    transitions = Attribute("Transition objects container.")

    processPermissions = Attribute("Relevant permissions for the process "
                                   "definition")

    def addState(name, state):
        """Add a IState to the process definition."""

    def getState(name):
        """Get the named state."""

    def removeState(name):
        """Remove a state from the process definition

        Raises ValueError exception if trying to delete the initial state.
        """

    def getStateNames():
        """Get the state names."""

    def getInitialStateName():
        """Get the name of the initial state."""

    def addTransition(name, transition):
        """Add a ITransition to the process definition."""

    def getTransition(name):
        """Get the named transition."""

    def removeTransition(name):
        """Remove a transition from the process definition."""

    def getTransitionNames():
        """Get the transition names."""

    def clear():
        """Clear the whole ProcessDefinition."""

    def addProcessPermission(p):
        """Add a process permission
        """

    def delProcessPermission(p):
        """Del a process permission
        """

    def getProcessPermissions():
        """Returns the process permissions"""

    def getAvailablePermissions():
        """Returns the permissions we may within this process definition
        """

class IStatefulPIAdapter(IPIAdapter):
    """Workflow process instance Adapter.

    Handles Behaviour for a process defined by a
    StatefulProcessDefinition.
    """

    def initialize():
        """Initialize the Process.

        set Initial State.
        """

    def getOutgoingTransitions():
        """Get the outgoing transitions."""

    def fireTransition(id):
        """Fire a outgoing transitions."""

class IContentProcessRegistry(Interface):
    """Content Type <-> Process Definitions Registry

    This is a registry for mapping content types (interface) to workflow
    process definitions (by name).
    """

    def register(iface, name):
        """Register a new process definition (name) for the interface iface."""

    def unregister(iface, name):
        """Unregister a process (name) for a particular interface."""

    def getProcessNamesForInterface(iface):
        """Return a list of process defintion names for the particular
        interface."""

    def getInterfacesForProcessName(name):
        """Return a list of interfaces for the particular process name."""

class IContentWorkflowsManager(IContentProcessRegistry):
    """A Content Workflows Manager.

    It associates content objects with some workflow process definitions.
    """

    def getProcessDefinitionNamesForObject(object):
        """Get the process definition names for a particular object.

        This method reads in all the interfaces this object implements and
        finds then the corresponding process names using the
        IContentProcessRegistry."""

####################################################################

class ITransitionEventUserTriggered(IObjectEvent):
    """ Transition event triggered by user interface
    """

    kwargs = Attribute('Mapping containing information coming from the form')
    form_action = Attribute('Form action')

####################################################################

class IProcessDefinitionAddPermissionsEvent(IObjectEvent):
    """Process Definition Add Permissions Event interface
    """
    permissions_to_add = Attribute("Permission to add the process definition")

class IProcessDefinitionDelPermissionsEvent(IObjectEvent):
    """Process Definition Dell Permissions Event interface
    """
    permissions_to_remove = Attribute("Permission to add the process"
                                      "definition")

####################################################################

class IStatePermissionsRolesMappingUpdateEvent(IObjectEvent):
    """State Permissions Roles Mapping Update interface
    """
    mapping = Attribute("The actual mapping containing permissions role")

####################################################################
