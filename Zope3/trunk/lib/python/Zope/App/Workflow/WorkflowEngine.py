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
from IWorkflowEngine import IWorkflowEngine

class WorkflowEngine:

    __implements__ =  IWorkflowEngine

    ############################################################
    # Implementation methods for interface
    # Zope.App.Workflow.IWorkflowEngine

    def getProcessInstance(self, process_id):
        '''See interface IWorkflowEngine'''

    def getWorklist(self, user, process_instance=None):
        '''See interface IWorkflowEngine'''

    def listProcessInstances(self):
        '''See interface IWorkflowEngine'''
    #
    ############################################################
