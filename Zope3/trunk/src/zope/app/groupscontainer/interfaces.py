##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Zope Groups Folder Interface"""

# $Id: interfaces.py 27237 2004-10-12 09:33:00 mriya3 $

from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ContainerTypesConstraint
from zope.app.container.constraints import ItemTypePrecondition
from zope.security.interfaces import IGroup
from zope.schema import Field, TextLine
from zope.interface import Interface

class IGroupsFolder(IContainer):
       
    def getGroupsForPrincipal(principalid):
        """Get groups the given principal belongs to"""
        
    def getPrincipalsForGroup(groupid):
        """Get principals which belong to the group"""
        
    def __setitem__(name, object):
        """Adds a Group to the GroupFolder"""

    __setitem__.precondition = ItemTypePrecondition(IGroup)

class IGroupContained(IContained):
    __parent__ = Field(
             constraint = ContainerTypesConstraint(IGroupsFolder))
             

class IGroupSearchCriteria(Interface):
    search = TextLine(title=u"Group Search String")

