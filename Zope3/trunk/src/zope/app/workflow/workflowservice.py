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
from zope.app.interfaces.workflow import IWorkflowService

class WorkflowService:

    __implements__ =  IWorkflowService

    engines = ()

    def removeEngine(self, engine):
        '''See interface IWorkflowService'''
        self.engines = tuple(filter(lambda x: x != engine, self.engines))

    def listWorkflowEngineActions(self):
        '''See interface IWorkflowService'''
        result = []
        for engine in self.engines:
            result.extend(engine.listActions())
        return result

    def listEngine(self):
        '''See interface IWorkflowService'''
        return self.engines

    def addEngine(self, engine):
        '''See interface IWorkflowService'''

        self.engines = self.engines + (engine,)

    def getEngine(self, interface):
        '''See interface IWorkflowService'''

        result = []
        for engine in self.engines:
            if interface.isImplementedBy(engine):
                result.append(engine)
        return result
