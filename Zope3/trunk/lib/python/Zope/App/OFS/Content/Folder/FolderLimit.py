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

Revision information: 
$Id: FolderLimit.py,v 1.2 2002/06/10 23:28:00 jim Exp $
"""

from Zope.App.OFS.Container.IContainerLimit import IContainerLimit
from Zope.App.OFS.Container.Exceptions import UnaddableError


class FolderLimitExceededError(UnaddableError):
    """Exception that is raised, when the limit of the folder was
       reached."""
    pass


class FolderLimit:
    """Implements a feature that allows to restrict the amount of items in
       a Folder.
    """

    __implements__ =  IContainerLimit

    _limit = 1000

    ############################################################
    # Implementation methods for interface
    # Zope.App.OFS.IContainerLimit

    def setLimit(self, limit):
        '''See interface IContainerLimit'''
        self._limit = limit


    def getLimit(self):
        '''See interface IContainerLimit'''
        return self._limit


    def isLimitReached(self):
        '''See interface IContainerLimit'''
        if len(self) >= self._limit:
            return 1
        else:
            return 0

    #
    ############################################################
