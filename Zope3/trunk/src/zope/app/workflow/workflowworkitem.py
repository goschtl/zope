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
from zope.app.interfaces.workflow import IWorkflowWorkitem, \
     WorkflowWorkitemException, \
     INIT, BEGUN, COMPLETED, FAILED

class WorkflowWorkitem:

    __implements__ =  IWorkflowWorkitem

    def __init__(self, process_instance):
        self._process_instance = process_instance
        self._assignee = None
        self._state = INIT

    def getProcessInstance(self):
        '''See interface IWorkflowWorkitem'''
        return self._process_instance

    def begin(self, data=None):
        '''See interface IWorkflowWorkitem'''
        if self._state is not INIT:
            raise WorkflowWorkitemException
        self._state = BEGUN

    def complete(self, data=None):
        '''See interface IWorkflowWorkitem'''
        if self._state is not BEGUN:
            raise WorkflowWorkitemException
        self._state = COMPLETED

    def fail(self, data=None):
        '''See interface IWorkflowWorkitem'''
        if self._state is not BEGUN:
            raise WorkflowWorkitemException
        self._state = FAILED

    def assign(self, assignee, data=None):
        '''See interface IWorkflowWorkitem'''
        if self._state in (COMPLETED, FAILED):
            raise WorkflowWorkitemException
        self._assignee = assignee

    def getState(self):
        '''See interface IWorkflowWorkitem'''
        return self._state

    def getAssignee(self):
        '''See interface IWorkflowWorkitem'''
        return self._assignee
