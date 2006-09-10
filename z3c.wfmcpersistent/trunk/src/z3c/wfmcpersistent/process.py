##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
        return "TransitionDefinitionPersistent(from=%r, to=%r)" %(self.from_, self.to)


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

    def __repr__(self):
        return "ProcessPersistent(%r)" % self.process_definition_identifier

class Application(zope.wfmc.process.Application, Persistent):

    def __repr__(self):
        input = u', '.join([param.__name__ for param in self.parameters
                           if param.input == True])
        output = u', '.join([param.__name__ for param in self.parameters
                           if param.output == True])        
        return "<ApplicationPersistent %r: (%s) --> (%s)>" %(self.__name__, input, output)
        

class Participant(zope.wfmc.process.Participant, Persistent):

    def __repr__(self):
        return "ParticipantPersistent(%r)" %self.__name__
