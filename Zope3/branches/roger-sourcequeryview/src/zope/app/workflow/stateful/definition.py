##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Stateful workflow process definition.

$Id$
"""
from persistent import Persistent
from persistent.dict import PersistentDict

from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.security.checker import CheckerPublic

from zope.app.container.interfaces import IReadContainer
from zope.app.container.contained import Contained, containedEvent
from zope.event import notify
from zope.app.event.objectevent import ObjectEvent, modified
from zope.app.workflow.definition import ProcessDefinition
from zope.app.workflow.definition import ProcessDefinitionElementContainer
from zope.app.workflow.stateful.interfaces import IStatefulProcessDefinition
from zope.app.workflow.stateful.interfaces import IState, ITransition, INITIAL
from zope.app.workflow.stateful.interfaces import IStatefulStatesContainer
from zope.app.workflow.stateful.interfaces import IStatefulTransitionsContainer
from zope.app.workflow.stateful.interfaces import MANUAL
from zope.app.workflow.stateful.instance import StatefulProcessInstance


class State(Persistent, Contained):
    """State."""
    implements(IState)


class StatesContainer(ProcessDefinitionElementContainer):
    """Container that stores States."""
    implements(IStatefulStatesContainer)


class StateNamesVocabulary(SimpleVocabulary):
    """Vocabulary providing the names of states in a local process definition.
    """

    def __init__(self, context):
        terms = [SimpleTerm(name) for name in self._getStateNames(context)]
        super(StateNamesVocabulary, self).__init__(terms)

    def _getStateNames(self, context):
        if hasattr(context, 'getProcessDefinition'):
            return context.getProcessDefinition().getStateNames()
        else:
            for obj in zapi.getParents(context):
                if IStatefulProcessDefinition.providedBy(obj):
                    return obj.getStateNames()
        raise 'NoLocalProcessDefinition', 'No local process definition found.'


class Transition(Persistent, Contained):
    """Transition from one state to another."""

    implements(ITransition)

    # See ITransition
    sourceState = None
    destinationState = None
    condition = None
    script = None
    permission = CheckerPublic
    triggerMode = MANUAL

    def __init__(self, sourceState=None, destinationState=None, condition=None,
                 script=None, permission=CheckerPublic, triggerMode=None):
        super(Transition, self).__init__()
        self.sourceState = sourceState
        self.destinationState = destinationState
        self.condition = condition or None
        self.script = script or None
        self.permission = permission or None
        self.triggerMode = triggerMode

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
        self._publishModified('transitions', self.__transitions)
        self._publishModified('states', self.__states)
        # See workflow.stateful.IStatefulProcessDefinition
        self.schemaPermissions = PersistentDict()

    _clear = clear = __init__

    def _publishModified(self, name, object):
        object, event = containedEvent(object, self, name)
        if event:
            notify(event)
            modified(self)

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

        # TODO:
        # Process instances need to have a place, so they can look things
        # up.  It's not clear to me (Jim) what place they should have.

        # The parent of the process instance should be the object it is
        # created for!!! This will cause all sorts of head-aches, but at this
        # stage we do not have the object around; it would need some API
        # changes to do that. (SR)
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
        """See zope.app.container.interfaces.IReadContainer"""
        return iter(self.keys())

    def keys(self):
        """See zope.app.container.interfaces.IReadContainer"""
        return ['states', 'transitions']

    def values(self):
        """See zope.app.container.interfaces.IReadContainer"""
        return map(self.get, self.keys())

    def items(self):
        """See zope.app.container.interfaces.IReadContainer"""
        return [(key, self.get(key)) for key in self.keys()]

    def __len__(self):
        """See zope.app.container.interfaces.IReadContainer"""
        return 2

