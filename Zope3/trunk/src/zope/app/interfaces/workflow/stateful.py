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
"""Interfaces for stateful workflow process definition.

$Id: stateful.py,v 1.21 2004/02/24 14:25:37 srichter Exp $
"""
import zope.schema
from zope.app.security.permission import PermissionField

from zope.interface import Interface, Attribute
from zope.app.component.interfacefield import InterfaceField
from zope.app.interfaces.workflow import IWorkflowEvent
from zope.app.interfaces.workflow import IProcessDefinition
from zope.app.interfaces.workflow import IProcessInstance
from zope.app.interfaces.workflow import IProcessDefinitionElementContainer

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


class IRelevantDataChangeEvent(IWorkflowEvent):
    """This event is fired, when the object's data changes and the data is
    considered 'relevant' to the workflow. The attributes of interest are
    usually defined by a so called Relevant Data Schema."""

    process = Attribute("""The process instance that is doing the
                           transition. Note that this object really represents
                           the workflow.""")

    schema = Attribute("""The schema that defines the relevant data
                          attributes.""")

    attributeName = Attribute("""Name of the attribute that is changed.""")

    oldValue = Attribute("""The old value of the attribute.""")

    newValue = Attribute("""The new value of the attribute.""")


class IBeforeRelevantDataChangeEvent(IRelevantDataChangeEvent):
    """This event is triggered before some of the workflow-relevant data is
    being changed."""


class IAfterRelevantDataChangeEvent(IRelevantDataChangeEvent):
    """This event is triggered after some of the workflow-relevant data has
    been changed."""


class IState(Interface):
    """Interface for state of a stateful workflow process definition."""
    # XXX Should at least have a title, if not a value as well

class IStatefulStatesContainer(IProcessDefinitionElementContainer):
    """Container that stores States."""



class AvailableStatesField(zope.schema.TextLine):
    """Available States."""

    def __allowed(self):
        pd = self.context.getProcessDefinition()
        return pd.getStateNames()

    allowed_values = property(__allowed)


class TriggerModeField(zope.schema.TextLine):
    """Trigger Mode."""

    def __allowed(self):
        return [MANUAL, AUTOMATIC]

    allowed_values = property(__allowed)


class ITransition(Interface):
    """Stateful workflow transition."""

    sourceState = AvailableStatesField(
        title=u"Source State",
        description=u"Name of the source state.",
        required=True)

    destinationState = AvailableStatesField(
        title=u"Destination State",
        description=u"Name of the destination state.",
        required=True)

    condition = zope.schema.TextLine(
        title=u"Condition",
        description=u"""The condition that is evaluated to decide if the
                        transition can be fired or not.""",
        required=False)

    script = zope.schema.TextLine(
        title=u"Script",
        description=u"""The script that is evaluated to decide if the
                        transition can be fired or not.""",
        required=False)

    # XXX cannot add a default value -> raises
    # ComponentLookupError: Permissions
    # required=False does not help as well
    # so for now the permission needs to be set ttw
    # till we find another solution
    permission = PermissionField(
        title=u"The permission needed to fire the Transition.",
        required=True)


    triggerMode = TriggerModeField(
        title=u"Trigger Mode",
        description=u"How the Transition is triggered (Automatic/Manual)",
        default=u"Manual")


    def getSourceState():
        """Get Source State."""

    def setSourceState(source):
        """Set Source State."""

    def getDestinationState():
        """Get Destination State."""

    def setDestinationState(destination):
        """Set Destination State."""

    def getCondition():
        """Get Condition."""

    def setCondition(condition):
        """Set Condition."""

    def getScript():
        """Get Script."""

    def setScript(script):
        """Set Script."""

    def getPermission():
        """Get Permission."""

    def setPermission(permission):
        """Set Permission."""

    def getTriggerMode():
        """Return the TriggerMode."""

    def setTriggerMode():
        """Set TriggerMode."""

    def getProcessDefinition():
        """Return the ProcessDefinition Object."""


class IStatefulTransitionsContainer(IProcessDefinitionElementContainer):
    """Container that stores Transitions."""


class IStatefulProcessDefinition(IProcessDefinition):
    """Interface for stateful workflow process definition."""

    relevantDataSchema = InterfaceField(
        title=u"Workflow-Relevant Data Schema",
        description=u"Specifies the schema that characterizes the workflow "
                    u"relevant data of a process instance, found in pd.data.",
        default=None,
        required=False)

    schemaPermissions = Attribute(u"A dictionary that maps set/get permissions"
                                  u"on the schema's fields. Entries looks as"
                                  u"follows: {fieldname:(set_perm, get_perm)}")

    states = Attribute("State objects container.")

    transitions = Attribute("Transition objects container.")

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

    # XXX Temporarily till we find a better solution
    def clear():
        """Clear the whole ProcessDefinition."""



class IStatefulProcessInstance(IProcessInstance):
    """Workflow process instance.

    Represents the instance of a process defined by a
    StatefulProcessDefinition.
    """

    data = Attribute("Relevant Data object.")

    def initialize():
        """Initialize the ProcessInstance.

        set Initial State and create relevant Data.
        """

    def getOutgoingTransitions():
        """Get the outgoing transitions."""

    def fireTransition(id):
        """Fire a outgoing transitions."""

    def getProcessDefinition():
        """Get the process definition for this instance."""


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

    def subscribe():
        """Subscribe to the prevailing object hub service."""

    def unsubscribe():
        """Unsubscribe from the object hub service."""

    def isSubscribed():
        """Return whether we are currently subscribed."""

    def getProcessDefinitionNamesForObject(object):
        """Get the process definition names for a particular object.

        This method reads in all the interfaces this object implements and
        finds then the corresponding process names using the
        IContentProcessRegistry."""
