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
from zope.app.interfaces.workflow import IWorkflowProcessInstance

class WorkflowProcessInstance:

    __implements__ =  IWorkflowProcessInstance

    def listActiveWorkitems(self):
        '''See interface IWorkflowProcessInstance'''

    def setActive(self):
        '''See interface IWorkflowProcessInstance'''

    def listWorkitems(self):
        '''See interface IWorkflowProcessInstance'''

    def listFailedWorkitems(self):
        '''See interface IWorkflowProcessInstance'''

    def getStatus(self):
        '''See interface IWorkflowProcessInstance'''

    def setCompleted(self):
        '''See interface IWorkflowProcessInstance'''
