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
"""Home Directory of a User

$Id$
"""
__docformat__ = "reStructuredText"
from persistent import Persistent
from BTrees.OOBTree import OOBTree

from zope.interface import implements

from zope.app import zapi
from zope.app.container.contained import Contained
from zope.app.folder import Folder
from zope.app.securitypolicy.interfaces import IPrincipalRoleManager

from zope.app.homefolder.interfaces import IHomeFolder, IHomeFolderManager

class HomeFolderManager(Persistent, Contained):
    """ """
    implements(IHomeFolderManager)

    # See IHomeFolderManager
    homeFolderBase = None
    createHomeFolder = True
    autoCreateAssignment = False
    homeFolderRole = u'zope.Manager'

    def __init__(self):
        self.assignments = OOBTree()

    def assignHomeFolder(self, principalId, folderName=None, create=None):
        """See IHomeFolderManager"""
        # The name of the home folder is folderName, if specified, otherwise
        # it is the principal id
        name = folderName or principalId
        # Make the assignment.
        self.assignments[principalId] = name

        # Create a home folder instance, if the correct flags are set.
        if (create is True) or (create is None and self.createHomeFolder):
            if name not in self.homeFolderBase:
                self.homeFolderBase[name] = Folder()
            principal_roles = IPrincipalRoleManager(self.homeFolderBase[name])
            principal_roles.assignRoleToPrincipal(
                self.homeFolderRole, principalId)


    def unassignHomeFolder(self, principalId, delete=False):
        """See IHomeFolderManager"""
        folderName = self.assignments[principalId]
        if delete is True:
            del self.homeFolderBase[folderName]
        del self.assignments[principalId]


    def getHomeFolder(self, principalId):
        """See IHomeFolderManager"""
        if principalId not in self.assignments:
            if self.autoCreateAssignment:
                self.assignHomeFolder(principalId, create=True)
            else:
                return None
        
        return self.homeFolderBase.get(self.assignments[principalId], None)


class HomeFolder(object):
    """Home folder adapter for a principal."""
    implements(IHomeFolder)

    def __init__(self, principal):
        self.principal = principal

    homeFolder = property(lambda self: getHomeFolder(self.principal))


def getHomeFolder(principal):
    """Get the home folder instance of the principal."""
    principalId = principal.id
    for name, manager in zapi.getUtilitiesFor(IHomeFolderManager):
        folder = manager.getHomeFolder(principalId)
        if folder is not None:
            return folder

    return None
    
