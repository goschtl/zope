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
from zope.app.interfaces.workflow import IWorkflowActivityInfo

class WorkflowActivityInfo:

    __implements__ = IWorkflowActivityInfo

    def __init__(self, id,
                 title='',
                 category='',
                 action_url='',
                 permissions=(),
                 roles=(),
                 condition=None,
                 source=None,
                 ):
        self.id = id
        self._title = title
        self._category = category
        self._action_url = action_url
        self._permissions = permissions
        self._roles = roles
        self._condition = condition
        self._source = source

    def getId(self):
        '''See interface IWorkflowActivityInfo'''
        return self.id

    def getTitle(self):
        '''See interface IWorkflowActivityInfo'''
        return self._title

    def getCategory(self):
        '''See interface IWorkflowActivityInfo'''
        return self._category

    def getActionURL(self):
        '''See interface IWorkflowActivityInfo'''
        return self._action_url

    def getPermissions(self):
        '''See interface IWorkflowActivityInfo'''
        return self._permissions

    def getRoles(self):
        '''See interface IWorkflowActivityInfo'''
        return self._roles

    def getCondition(self):
        '''See interface IWorkflowActivityInfo'''
        return self._condition

    def getSource(self):
        '''See interface IWorkflowActivityInfo'''
        return self._source
