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
"""Zope Group implementation

$Id: group.py 27237 2004-10-12 09:33:00 mriya3 $

"""

from zope.security.interfaces import IGroup
from zope.app.pas.interfaces import IAuthenticatedPrincipalCreated
from persistent import Persistent
from zope.interface import implements, alsoProvides
from zope.app.groupscontainer.interfaces import IGroupContained, IGroupFolder
from zope.security.interfaces import IGroupAwarePrincipal
from types import StringTypes
import zope.app.zapi
from zope.event import notify


class Group(Persistent):

    implements(IGroup, IGroupContained)
    
    __parent__ = __name__ = None
    
    def __init__(self, id='', title='', description='', principalsids=[]):
        self.id = id
        self.title = title
        self.description = description
        self.__principals = principalsids
        
    def addPrincipals(self, *principalIds):
        tmpNewList = self.__principals
        for principalId in principalIds:
            if not principalId in self.__principals:
                tmpNewList.append(principalId)
        self.setPrincipals(tmpNewList)
        if self.__parent__ is not None:
            self.__parent__.updateMappingForPrincipals(*principalIds)

    def removePrincipals(self, *principalIds):
        tmpNewList = self.__principals
        for principalId in principalIds:
            if principalId in tmpNewList:
                tmpNewList.remove(principalId)
        self.setPrincipals(tmpNewList)
        if self.__parent__ is not None:
            self.__parent__.updateMappingForPrincipals(*principalIds)
        
    def containsPrincipal(self, principalId):
        return principalId in self.__principals
        
    def getPrincipals(self):
        return self.__principals
        
    def setPrincipals(self, prinlist):
        origprincipals = self.__principals
        self.__principals = prinlist
        
    principals = property(getPrincipals, setPrincipals)
    

def setGroupsForPrincipal(event):
    """Set group information when a principal is created"""
    principal = event.principal
    alsoProvides(principal, IGroupAwarePrincipal)
    principal.groups = []
    groupfolders = zope.app.zapi.getUtilitiesFor(IGroupFolder)
    for name, groupfolder in groupfolders:
        groups = groupfolder.getGroupsForPrincipal(principal.id)
        principal.groups.extend(groups)
