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

$Id: stateful.py,v 1.8 2003/03/22 16:02:46 jack-e Exp $
"""
import zope.schema
from zope.proxy.context import ContextProperty
from zope.app.security.permission import PermissionField

from zope.interface import Interface, Attribute
from zope.app.interfaces.workflow import IProcessDefinition
from zope.app.interfaces.workflow import IProcessInstance
from zope.app.interfaces.workflow import IProcessDefinitionElementContainer


class IState(Interface):
    """Interface for state of a stateful workflow process definition.
    """


class IStatefulStatesContainer(IProcessDefinitionElementContainer):
    """Container that stores States.
    """



class AvailableStatesField(zope.schema.TextLine):
    """Available States.
    """

    def __allowed(self):
        pd = self.context.getProcessDefinition()
        return pd.getStateNames()

    allowed_values = ContextProperty(__allowed)


class ITransition(Interface):
    """Stateful workflow transition.
    """

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
                        condition is fired or not.""",
        required=False)

    permission = PermissionField(
        title=u"The permission needed to fire the Transition.")


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

    def getPermission():
        """Get Permission."""

    def setPermission(permission):
        """Set Permission."""

    def getProcessDefinition():
        """Return the ProcessDefinition Object.
        """



class IStatefulTransitionsContainer(IProcessDefinitionElementContainer):
    """Container that stores Transitions.
    """




class IStatefulProcessDefinition(IProcessDefinition):
    """Interface for stateful workflow process definition.
    """

    # XXX How to specify permissions for RelevantData ??

    relevantDataSchema = zope.schema.TextLine(
        title=u"RelevantData Schema",
        description=u"Dotted Name of RelevantData Schema.",
        required=True)


    def setRelevantDataSchema(schema):
        """Set the Schema for RelevantData.
        """

    def getRelevantDataSchema():
        """Return the Schema for RelevantData.
        """



    states = Attribute("State objects container.")

    transitions = Attribute("Transition objects container.")

    def addState(name, state):
        """Add a IState to the process definition.
        """
    
    def getState(name):
        """Get the named state.
        """
    
    def removeState(name):
        """Remove a state from the process definition
    
        Raises ValueError exception if trying to delete the initial state.
        """
    
    def getStateNames():
        """Get the state names.
        """
    
    def getInitialStateName():
        """Get the name of the initial state.
        """
    
    def addTransition(name, transition):
        """Add a ITransition to the process definition.
        """
    
    def getTransition(name):
        """Get the named transition.
        """
    
    def removeTransition(name):
        """Remove a transition from the process definition.
        """
    
    def getTransitionNames():
        """Get the transition names.
        """



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
        """Get the outgoing transitions.
        """

    def fireTransition(id):
        """Fire a outgoing transitions.
        """



class IContentWorkflowsUtility(Interface):
    """A Content Workflows Utility.

    it associates content objects with some workflow process definitions.
    """

    def subscribe():
        """Subscribe to the prevailing object hub service.
        """

    def unsubscribe():
        """Unsubscribe from the object hub service.
        """

    def isSubscribed():
        """Return whether we are currently subscribed.
        """

    def getProcessDefinitionNames():
        """Get the process definition names.
        """

    def setProcessDefinitionNames(names):
        """Set the process definition names.
        """
