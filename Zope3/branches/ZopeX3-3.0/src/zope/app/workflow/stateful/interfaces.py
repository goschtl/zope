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
from zope.app.workflow.interfaces import IWorkflowEvent
from zope.app.workflow.interfaces import IProcessDefinition
from zope.app.workflow.interfaces import IProcessInstance
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
    # TODO: Should at least have a title, if not a value as well

class IStatefulStatesContainer(IProcessDefinitionElementContainer):
    """Container that stores States."""



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


class IStatefulProcessDefinition(IProcessDefinition):
    """Interface for stateful workflow process definition."""

    relevantDataSchema = zope.schema.Choice(
        title=_(u"Workflow-Relevant Data Schema"),
        description=_(u"Specifies the schema that characterizes the workflow "
                    u"relevant data of a process instance, found in pd.data."),
        vocabulary="Interfaces",
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

    def getProcessDefinitionNamesForObject(object):
        """Get the process definition names for a particular object.

        This method reads in all the interfaces this object implements and
        finds then the corresponding process names using the
        IContentProcessRegistry."""
