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
"""Zope Groups Folder implementation

$Id: groupfolder.py 27237 2004-10-12 09:33:00 mriya3 $

"""

from zope.app.groupscontainer.interfaces import IGroupSearchCriteria
from zope.app.groupscontainer.interfaces import IGroupFolder
from zope.app.pas.interfaces import IQuerySchemaSearch
from zope.app.container.btree import BTreeContainer
from zope.interface import implements
from BTrees.OOBTree import OOBTree
import zope.schema



class GroupFolder(BTreeContainer):

    implements(IGroupFolder, IQuerySchemaSearch)
    schema = (IGroupSearchCriteria)
    
    def __init__(self):
        super(BTreeContainer,self).__init__()
        # __inversemapping is used to map principals to groups
        self.__inverseMapping = OOBTree()

    def __delitem__(self, name):
        """Removes a group and updates the inverse mapping"""
        for principal in self.__inverseMapping.keys():
            groupListForPrincipal = self.__inverseMapping[principal]
            if name in groupListForPrincipal:
                groupListForPrincipal.remove(name)
        # Clean up 
        for principal in self.__inverseMapping.keys():
            groupListForPrincipal = self.__inverseMapping[principal]
            if len(groupListForPrincipal) == 0:
                del self.__inverseMapping[principal]
        super(BTreeContainer,self).__delitem__(name)
                
    def __setitem__(self, name, object):
        """Adds a new group and updates the inverse mapping"""
        super(BTreeContainer,self).__setitem__(name, object)
        principalsInGroup = object.principals
        for principal in principalsInGroup:
            if self.__inverseMapping.has_key(principal):
                self.__inverseMapping[principal].append(name)
            else:
                self.__inverseMapping[principal] = [name]        
   
    def getGroupsForPrincipal(self, principalid):
        """Get groups the given principal belongs to"""
        if self.__inverseMapping.has_key(principalid):
            return self.__inverseMapping[principalid]
        else:
            return []
        
        
    def getPrincipalsForGroup(self, groupid):
        """Get principals which belong to the group"""
        if groupid in self.keys():
            return self.__getitem__(groupid).principals
        else:
            return []
            
    def removePrincipalFromAllGroups(self, principalId):
        """Removes a principal from all the groups"""
        groupsItIsIn = self.getGroupsForPrincipal(principalId)
        for groupid in groupsItIsIn:
            self.__getitem__(groupid).removePrincipals(principalId)
                
    def getAllMappedPrincipals(self):
        """Returns all mapped principals"""
        return list(self.__inverseMapping.keys())
        
    def updateMappingForPrincipals(self, *principalsIds):
        for principalId in principalsIds:
            self.updateMappingForPrincipal(principalId)
        
    def updateMappingForPrincipal(self, principalId):
        """Updates inverse mapping for principalId -> group"""
        tmpNewGroupList = []
        # Search in all groups and add to inverse mapping if the principalId is in 
        for groupid in self.keys():
            if self.__getitem__(groupid).containsPrincipal(principalId):
                tmpNewGroupList.append(groupid)
        # If the principal disappears from all groups just remove it
        if len(tmpNewGroupList) == 0:
            del self.__inverseMapping[principalId]
        else:
            self.__inverseMapping[principalId] = tmpNewGroupList

    def search(self, query, start=None, batch_size=None):
        """ Search for groups"""
        search = query.get('search')
        if search is not None:
            i = 0
            n = 0
            for value in self.keys():
                if search in value:
                    if not ((start is not None and i < start)
                            or
                            (batch_size is not None and n > batch_size)):
                        n += 1
                        yield value
                i += 1
        
    def principalInfo(self, id):
        if id in self:
            return {'title': self[id].title, 'description': self[id].description}
        
        
            
