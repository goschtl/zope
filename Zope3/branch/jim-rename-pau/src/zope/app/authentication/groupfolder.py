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

$Id$

"""

try:
    set
except NameError:
    from sets import Set as set

from BTrees.OOBTree import OOBTree
from persistent import Persistent

import zope.interface
import zope.schema

from zope.app import zapi
from zope.app.container.btree import BTreeContainer
import zope.app.container.constraints
from zope.app.container.interfaces import IContained, IContainer
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.authentication.interfaces import IAuthenticatedPrincipalCreated
from zope.app.authentication.interfaces import IPrincipalSearchPlugin
from zope.app.authentication.interfaces import IQuerySchemaSearch
import zope.app.security.vocabulary
        
class IGroupInformation(zope.interface.Interface):

    title = zope.schema.TextLine(
        title=_("Title"),
        description=_("Provides a title for the permission."),
        required=True)

    description = zope.schema.Text(
        title=_("Description"),
        description=_("Provides a description for the permission."),
        required=False)

    principals = zope.schema.List(
        title=_("Principals"),
        value_type=zope.schema.Choice(
            source=zope.app.security.vocabulary.PrincipalSource()),
        description=_(
        "List of principal ids of principals which belong to the group"),
        required=False)
        
class IGroupFolder(IContainer, IQuerySchemaSearch):

    zope.app.container.constraints.contains(IGroupInformation)

    prefix = zope.schema.TextLine(
        title=u"Group ID prefix",
        description=u"Prefix added to IDs of groups in this folder",
        readonly=True,
        )
       
    def getGroupsForPrincipal(principalid):
        """Get groups the given principal belongs to"""
        
    def getPrincipalsForGroup(groupid):
        """Get principals which belong to the group"""
        
class IGroupContained(IContained):

    zope.app.container.constraints.containers(IGroupFolder)
             

class IGroupSearchCriteria(zope.interface.Interface):

    search = zope.schema.TextLine(
        title=u"Group Search String",
        required=False,
        missing_value=u'',
        )


class GroupFolder(BTreeContainer):

    zope.interface.implements(IGroupFolder)
    schema = (IGroupSearchCriteria)
    
    def __init__(self, prefix=u''):
        self.prefix=prefix
        super(BTreeContainer,self).__init__()
        # __inversemapping is used to map principals to groups
        self.__inverseMapping = OOBTree()

    def __setitem__(self, name, value):
        BTreeContainer.__setitem__(self, name, value)
        group_id = self._groupid(value)
        for principal_id in value.principals:
            self._addPrincipalToGroup(principal_id, group_id)

    def __delitem__(self, name):
        value = self[name]
        group_id = self._groupid(value)
        for principal_id in value.principals:
            self._removePrincipalFromGroup(principal_id, group_id)
        BTreeContainer.__delitem__(self, name)

    def _groupid(self, group):
        return self.prefix+group.__name__

    def _addPrincipalToGroup(self, principal_id, group_id):
        self.__inverseMapping[principal_id] = (
            self.__inverseMapping.get(principal_id, ())
            + (group_id,))

    def _removePrincipalFromGroup(self, principal_id, group_id):
        groups = self.__inverseMapping.get(principal_id)
        if groups is None:
            return
        new = tuple([id for id in groups if id != group_id])
        if new:
            self.__inverseMapping[principal_id] = new
        else:
            del self.__inverseMapping[principal_id]
   
    def getGroupsForPrincipal(self, principalid):
        """Get groups the given principal belongs to"""
        return self.__inverseMapping.get(principalid, ())
        

    def search(self, query, start=None, batch_size=None):
        """ Search for groups"""
        search = query.get('search')
        if search is not None:
            i = 0
            n = 0
            search = search.lower()
            for id, groupinfo in self.items():
                if (search in groupinfo.title.lower() or
                    search in groupinfo.description.lower()):
                    if not ((start is not None and i < start)
                            or
                            (batch_size is not None and n >= batch_size)):
                        n += 1
                        yield self.prefix+id
                i += 1
        
    def principalInfo(self, id):
        if id.startswith(self.prefix):
            id = id[len(self.prefix):]
            info = self.get(id)
            if info is not None:
                return {'title': info.title,
                        'description': info.description,
                        }

class GroupCycle(Exception):
    """There is a cyclic relationship among groups
    """

class InvalidPrincipalIds(Exception):
    """A user has a group id for a group that can't be found
    """

class InvalidGroupId(Exception):
    """A user has a group id for a group that can't be found
    """

def nocycles(principal_id, seen, getPrincipal):
    if principal_id in seen:
        if principal_id in seen:
            raise GroupCycle(principal_id, seen)
    seen.append(principal_id)
    principal = getPrincipal(principal_id)
    for group_id in principal.groups:
        nocycles(group_id, seen, getPrincipal)
    seen.pop()

class GroupInformation(Persistent):

    zope.interface.implements(IGroupInformation, IGroupContained)
    
    __parent__ = __name__ = None

    _principals = ()
    
    def __init__(self, title='', description=''):
        self.title = title
        self.description = description
        
    def setPrincipals(self, prinlist):
        parent = self.__parent__
        if parent is not None:
            old = set(self._principals)
            new = set(prinlist)
            group_id = parent._groupid(self)
            
            for principal_id in old - new:
                try:
                    parent._removePrincipalFromGroup(principal_id, group_id)
                except AttributeError:
                    pass

            for principal_id in new - old:
                try:
                    parent._addPrincipalToGroup(principal_id, group_id)
                except AttributeError:
                    pass

            nocycles(group_id, [], zapi.principals().getPrincipal)

        self._principals = tuple(prinlist)
        
    principals = property(lambda self: self._principals, setPrincipals)

def setGroupsForPrincipal(event):
    """Set group information when a principal is created"""

    principal = event.principal
    try:
        groups = principal.groups
    except AttributeError:
        # If the principal doesn't support groups. then do nothing
        return
    
    groupfolders = zapi.getUtilitiesFor(IPrincipalSearchPlugin)
    for name, groupfolder in groupfolders:
        # It's annoying that we have to filter here, but there isn't
        # a good reason for people to register group folder utilities.
        if not isinstance(groupfolder, GroupFolder):
            continue
        principal.groups.extend(
            groupfolder.getGroupsForPrincipal(principal.id),
            )
