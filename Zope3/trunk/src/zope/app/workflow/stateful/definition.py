##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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

"""Stateful workflow process definition.

$Id: definition.py,v 1.8 2003/11/04 04:04:24 jeremy Exp $
"""
__metaclass__ = type

from persistence import Persistent
from persistence.dict import PersistentDict

from zope.app.interfaces.container import IReadContainer
from zope.app.interfaces.workflow.stateful import IStatefulProcessDefinition
from zope.app.interfaces.workflow.stateful import IState, ITransition, INITIAL
from zope.app.interfaces.workflow.stateful import IStatefulStatesContainer
from zope.app.interfaces.workflow.stateful import IStatefulTransitionsContainer
from zope.interface import implements

from zope.app.container.contained import Contained
from zope.app.workflow.definition import ProcessDefinition
from zope.app.workflow.definition import ProcessDefinitionElementContainer
from zope.app.workflow.stateful.instance import StatefulProcessInstance


class State(Persistent, Contained):
    """State."""
    implements(IState)


class StatesContainer(ProcessDefinitionElementContainer):
    """Container that stores States."""
    implements(IStatefulStatesContainer)


class Transition(Persistent, Contained):
    """Transition from one state to another."""

    implements(ITransition)

    def __init__(self, source=None, destination=None, condition=None,
                 script=None, permission=None, triggerMode=None):
        super(Transition, self).__init__()
        self.__source = source
        self.__destination = destination
        self.__condition = condition or None
        self.__script = script or None
        self.__permission = permission or None
        self.__triggerMode = triggerMode

    def getSourceState(self):
        return self.__source

    def setSourceState(self, source):
        self.__source = source

    def getDestinationState(self):
        return self.__destination

    def setDestinationState(self, destination):
        self.__destination = destination

    def getCondition(self):
        return self.__condition

    def setCondition(self, condition):
        self.__condition = condition or None

    def getScript(self):
        return self.__script

    def setScript(self, script):
        self.__script = script or None

    def getPermission(self):
        return self.__permission

    def setPermission(self, permission):
        self.__permission = permission or None

    def getTriggerMode(self):
        return self.__triggerMode

    def setTriggerMode(self, mode):
        self.__triggerMode = mode

    # See ITransition
    sourceState = property(getSourceState, setSourceState, None,
                           "Source State of Transition.")

    destinationState = property(getDestinationState, setDestinationState, None,
                                "Destination State of Transition.")

    condition = property(getCondition, setCondition, None,
                         "Condition for Transition.")

    script = property(getScript, setScript, None,
                         "Script for Transition.")

    permission = property(getPermission, setPermission, None,
                          "Permission for Transition.")

    triggerMode = property(getTriggerMode, setTriggerMode, None,
                           "TriggerMode for Transition.")

    def getProcessDefinition(self):
        return self.__parent__.getProcessDefinition()


class TransitionsContainer(ProcessDefinitionElementContainer):
    """Container that stores Transitions."""
    implements(IStatefulTransitionsContainer)


class StatefulProcessDefinition(ProcessDefinition):
    """Stateful workflow process definition."""

    implements(IStatefulProcessDefinition, IReadContainer)

    def __init__(self):
        super(StatefulProcessDefinition, self).__init__()
        self.__states = StatesContainer()
        initial = State()
        self.__states[self.getInitialStateName()] = initial
        self.__transitions = TransitionsContainer()
        self.__schema = None
        # See workflow.stateful.IStatefulProcessDefinition
        self.schemaPermissions = PersistentDict()

    _clear = clear = __init__

    def getRelevantDataSchema(self):
        return self.__schema

    def setRelevantDataSchema(self, schema):
        self.__schema = schema

    # See workflow.stateful.IStatefulProcessDefinition
    relevantDataSchema = property(getRelevantDataSchema,
                                  setRelevantDataSchema,
                                  None,
                                  "Schema for RelevantData.")

    # See workflow.stateful.IStatefulProcessDefinition
    states = property(lambda self: self.__states)

    # See workflow.stateful.IStatefulProcessDefinition
    transitions = property(lambda self: self.__transitions)

    def addState(self, name, state):
        """See workflow.stateful.IStatefulProcessDefinition"""
        if name in self.states:
            raise KeyError, name
        self.states[name] = state

    def getState(self, name):
        """See workflow.stateful.IStatefulProcessDefinition"""
        return self.states[name]

    def removeState(self, name):
        """See workflow.stateful.IStatefulProcessDefinition"""
        del self.states[name]

    def getStateNames(self):
        """See workflow.stateful.IStatefulProcessDefinition"""
        return self.states.keys()

    def getInitialStateName(self):
        """See workflow.stateful.IStatefulProcessDefinition"""
        return INITIAL

    def addTransition(self, name, transition):
        """See workflow.stateful.IStatefulProcessDefinition"""
        if name in self.transitions:
            raise KeyError, name
        self.transitions[name] = transition

    def getTransition(self, name):
        """See workflow.stateful.IStatefulProcessDefinition"""
        return self.transitions[name]

    def removeTransition(self, name):
        """See workflow.stateful.IStatefulProcessDefinition"""
        del self.transitions[name]

    def getTransitionNames(self):
        """See workflow.stateful.IStatefulProcessDefinition"""
        return self.transitions.keys()

    def createProcessInstance(self, definition_name):
        """See workflow.IProcessDefinition"""
        pi_obj = StatefulProcessInstance(definition_name)

        # XXX
        # Process instances need to have a place, so they can look things
        # up.  It's not clear to me (Jim) what place they should have.
        pi_obj.__parent__ = self


        pi_obj.initialize()
        return pi_obj


    def __getitem__(self, key):
        "See Interface.Common.Mapping.IReadMapping"

        result = self.get(key)
        if result is None:
            raise KeyError(key)

        return result


    def get(self, key, default=None):
        "See Interface.Common.Mapping.IReadMapping"

        if key == 'states':
            return self.states

        if key == 'transitions':
            return self.transitions

        return default


    def __contains__(self, key):
        "See Interface.Common.Mapping.IReadMapping"

        return self.get(key) is not None

    def __iter__(self):
        """See zope.app.interfaces.container.IReadContainer"""
        return iter(self.keys())

    def keys(self):
        """See zope.app.interfaces.container.IReadContainer"""
        return ['states', 'transitions']

    def values(self):
        """See zope.app.interfaces.container.IReadContainer"""
        return map(self.get, self.keys())

    def items(self):
        """See zope.app.interfaces.container.IReadContainer"""
        return [(key, self.get(key)) for key in self.keys()]

    def __len__(self):
        """See zope.app.interfaces.container.IReadContainer"""
        return 2

