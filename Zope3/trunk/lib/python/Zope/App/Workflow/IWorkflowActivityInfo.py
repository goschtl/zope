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
"""
Interface for Workflow Activity Info
WAI encapsulates what can be done at a given point.
"""

from Interface import Interface

class IWorkflowActivityInfo(Interface):
    """
    Base interface for Workflow Activity Info.
    """

    def getId():
        """
        Get the Activity Info id.
        """

    def getTitle():
        """
        Get the Activity Info title.
        """

    def getCategory():
        """
        Get the Activity Info category.
        Returns a string (usually 'workflow').
        """

    def getActionURL():
        """
        Get the Activity Info URL that should be called
        to trigger the action.
        Returns an unencoded URL.
        """

    def getPermissions():
        """
        Get the permissions this Activity Info is protected by.
        Returns a list of IPermission.
        The Activity Info is valid if any permission matches.
        """

    def getRoles():
        """
        Get the roles this Activity Info is protected by.
        Returns a list of IRole.
        The Activity Info is valid if any role matches.
        """

    def getCondition():
        """
        Get the guard this Activity Info is protected by.
        Returns a TALES expression (Interface ? XXX).
        """

    def getSource():
        """
        Get the actual action object this Activity Info is about,
        for instance a workitem (task-based workflow) or a transition
        (content-based workflow).
        """
