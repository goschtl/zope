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

$Id: stateful.py,v 1.5 2003/02/06 21:54:13 jack-e Exp $
"""
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



class ITransition(Interface):
    """Stateful workflow transition.
    """

    sourceState = Attribute("Name of the source state.")

    destinationState = Attribute("Name of the destination state.")

    condition = Attribute("""The condition that is evaluated to decide if \
                             the condition is fired or not.""")

    permission = Attribute("Permission for this Transition.")


class IStatefulTransitionsContainer(IProcessDefinitionElementContainer):
    """Container that stores Transitions.
    """




class IStatefulProcessDefinition(IProcessDefinition):
    """Interface for stateful workflow process definition.
    """

    # more methods/attributes to come
    # relevantData - Permissions (checker)

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

    def setSchema(schema):
        """Set the Schema for RelevantData.
        """

    def getSchema():
        """Return the Schema for RelevantData.
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
