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

$Id: definition.py,v 1.1 2003/05/08 17:27:19 jack-e Exp $
"""
__metaclass__ = type

from persistence import Persistent
from persistence.dict import PersistentDict

from zope.proxy.context import ContextMethod, ContextWrapper
from zope.proxy.context import getWrapperData, getWrapperContainer
from zope.proxy.context import getWrapperContext

from zope.app.interfaces.container import IReadContainer

from zope.app.interfaces.workflow import IProcessDefinition
from zope.app.interfaces.workflow.stateful import IStatefulProcessDefinition
from zope.app.interfaces.workflow.stateful import IState, ITransition
from zope.app.interfaces.workflow.stateful import IStatefulStatesContainer
from zope.app.interfaces.workflow.stateful import IStatefulTransitionsContainer

from zope.app.workflow.definition import ProcessDefinition
from zope.app.workflow.definition import ProcessDefinitionElementContainer
from zope.app.workflow.stateful.instance import StatefulProcessInstance



class State(Persistent):
    """State."""

    __implements__ = IState



class StatesContainer(ProcessDefinitionElementContainer):
    """Container that stores States.
    """
    __implements__ = IStatefulStatesContainer


class Transition(Persistent):
    """Transition."""

    __implements__ = ITransition

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
        return getWrapperContainer(self).getProcessDefinition()
    getProcessDefinition = ContextMethod(getProcessDefinition)

                    

class TransitionsContainer(ProcessDefinitionElementContainer):
    """Container that stores Transitions.
    """
    __implements__ = IStatefulTransitionsContainer



class StatefulProcessDefinition(ProcessDefinition):
    """Stateful workflow process definition."""

    __implements__ = IStatefulProcessDefinition, IReadContainer

    def __init__(self):
        super(StatefulProcessDefinition, self).__init__()
        self.__states = StatesContainer()
        initial = State()
        self.__states.setObject(self.getInitialStateName(), initial)
        self.__transitions = TransitionsContainer()
        self.__schema = None

    _clear = clear = __init__

    ############################################################
    # Implementation methods for interface
    # zope.app.interfaces.workflow.stateful.IStatefulProcessDefinition

    def getRelevantDataSchema(self):
        return self.__schema

    def setRelevantDataSchema(self, schema):
        self.__schema = schema

    relevantDataSchema = property(getRelevantDataSchema,
                                  setRelevantDataSchema,
                                  None,
                                  "Schema for RelevantData.")



    states = property(lambda self: self.__states)
    
    transitions = property(lambda self: self.__transitions)
    
    def addState(self, name, state):
        if name in self.states:
            raise KeyError, name
        self.states.setObject(name, state)
    
    def getState(self, name):
        return self.states[name]
    getState = ContextMethod(getState)
    
    def removeState(self, name):
        del self.states[name]
    
    def getStateNames(self):
        return self.states.keys()

    # XXX This shouldn't be hardcoded
    def getInitialStateName(self):
        return 'INITIAL'
    
    def addTransition(self, name, transition):
        if name in self.transitions:
            raise KeyError, name
        self.transitions.setObject(name, transition)
    
    def getTransition(self, name):
        return self.transitions[name]
    getTransition = ContextMethod(getTransition)
    
    def removeTransition(self, name):
        del self.transitions[name]
    
    def getTransitionNames(self):
        return self.transitions.keys()
    
    # IProcessDefinition

    def createProcessInstance(self, definition_name):
        pi_obj = StatefulProcessInstance(definition_name)
        ContextWrapper(pi_obj, self).initialize()
        return pi_obj
    createProcessInstance = ContextMethod(createProcessInstance)

    #
    ############################################################


    ############################################################
    # Implementation methods for interface
    # zope.app.interfaces.container.IReadContainer

    def __getitem__(self, key):
        "See Interface.Common.Mapping.IReadMapping"
 
        result = self.get(key)
        if result is None:
            raise KeyError(key)
 
        return result
    
    __getitem__ = ContextMethod(__getitem__)
 
    def get(self, key, default=None):
        "See Interface.Common.Mapping.IReadMapping"
 
        if key == 'states':
            return self.states
 
        if key == 'transitions':
            return self.transitions

        return default
 
    get = ContextMethod(get)
 
    def __contains__(self, key):
        "See Interface.Common.Mapping.IReadMapping"
 
        return self.get(key) is not None
 
    # Enumeration methods. We'll only expose Packages for now:
    def __iter__(self):
        return iter(self.keys())
 
    def keys(self):
        return ['states', 'transitions']
 
    def values(self):
        return map(self.get, self.keys())
 
    values = ContextMethod(values)
 
    def items(self):
        return [(key, self.get(key)) for key in self.keys()]
 
    items = ContextMethod(items)
 
    def __len__(self):
        return 2    


    #
    ############################################################
