##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Processes

$Id: process.py 38356 2005-09-07 19:34:16Z srichter $
"""

from persistent import Persistent
from persistent.list import PersistentList
from persistent.dict import PersistentDict

import zope.component

import z3c.wfmcpersistent.interfaces
import zope.wfmc.process

class TransitionDefinition(zope.wfmc.process.TransitionDefinition, Persistent):
    
    name = u''

    def __repr__(self):
        return "TransitionDefinitionPersistent(from=%r, to=%r)" %(self.from_,
                                                                  self.to)


class ProcessDefinition(zope.wfmc.process.ProcessDefinition, Persistent):
    
    TransitionDefinitionFactory = TransitionDefinition
    
    def __init__(self, id, integration=None):
        super(ProcessDefinition, self).__init__(id, integration)
        
        self.activities = PersistentDict()
        self.transitions = PersistentList()
        self.applications = PersistentDict()
        self.participants = PersistentDict()
    
    def __call__(self, context=None):
        return Process(self, self._start, context)

    def __repr__(self):
        return "ProcessDefinitionPersistent(%r)" % self.id

class ActivityDefinition(zope.wfmc.process.ActivityDefinition, Persistent):

    def __repr__(self):
        return "<ActivityDefinitionPersistent %r>" %self.__name__


class Process(zope.wfmc.process.Process):

    def definition(self):
        pdregistry = zope.component.getUtility(
            z3c.wfmcpersistent.interfaces.IProcessDefinitionRegistry,
            context=self.context,
            )
        return pdregistry.getProcessDefinition(
            self.process_definition_identifier)
    
    definition = property(definition)
    
    #Activity is buggy in zope.wfmc, until it's solved here is patched
    def transition(self, activity, transitions):
        if transitions:
            definition = self.definition

            for transition in transitions:
                activity_definition = definition.activities[transition.to]
                next = None
                if activity_definition.andJoinSetting:
                    # If it's an and-join, we want only one.
                    for i, a in self.activities.items():
                        if a.activity_definition_identifier == transition.to:
                            # we already have the activity -- use it
                            next = a
                            break

                if next is None:
                    next = Activity(self, activity_definition)
                    self.nextActivityId += 1
                    next.id = self.nextActivityId

                zope.event.notify(zope.wfmc.process.Transition(activity, next))
                self.activities[next.id] = next
                next.start(transition)
                #I want to be able to check the new WF states
                #that are determined by the workitems
                #therefore i need an event after the workitems are there
                zope.event.notify(TransitionDone(activity, next))

        if activity is not None:
            del self.activities[activity.id]
            if not self.activities:
                self._finish()

        self._p_changed = True
    #Activity is buggy in zope.wfmc, until it's solved here is patched

    def __repr__(self):
        return "ProcessPersistent(%r)" % self.process_definition_identifier

class Activity(zope.wfmc.process.Activity):
    #Activity is buggy in zope.wfmc, until it's solved here is patched
    def finish(self):
        zope.event.notify(zope.wfmc.process.ActivityFinished(self))

        definition = self.definition

        transitions = []
        for transition in definition.outgoing:
            if transition.condition(self.process.workflowRelevantData):
                transitions.append(transition)
                if not definition.andSplitSetting:
                    break # xor split, want first one
        
        #THIS is the difference
        if not transitions and definition.outgoing:
            raise zope.wfmc.interfaces.ProcessError(
                    "No valid transitions found")
        #THIS is the difference
        
        self.process.transition(self, transitions)
    #Activity is buggy in zope.wfmc, until it's solved here is patched

class Application(zope.wfmc.process.Application, Persistent):

    def __repr__(self):
        input = u', '.join([param.__name__ for param in self.parameters
                           if param.input == True])
        output = u', '.join([param.__name__ for param in self.parameters
                           if param.output == True])        
        return "<ApplicationPersistent %r: (%s) --> (%s)>" %(self.__name__,
                                                             input, output)
        

class Participant(zope.wfmc.process.Participant, Persistent):

    def __repr__(self):
        return "ParticipantPersistent(%r)" %self.__name__

class TransitionDone:
    #I want to be able to check the new WF states
    #that are determined by the workitems
    #therefore i need an event after the workitems are there
    def __init__(self, from_, to):
        self.from_ = from_
        self.to = to

    def __repr__(self):
        return "TransitionDone(%r, %r)" % (self.from_, self.to)
