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
Test IRolePermissionManager class.

$Id: RolePermissionManager.py,v 1.1 2002/06/20 15:55:01 jim Exp $
"""

from Zope.App.Security.IRolePermissionManager import IRolePermissionManager
from Zope.App.Security.Settings import Allow, Assign

class RolePermissionManager:

    __implements__ = IRolePermissionManager

    def __init__(self, **rp):
        self._rp = rp

    # Implementation methods for interface
    # Zope.App.Security.IRolePermissionManager.

    def getRolesForPermission(self, permission):
        '''See interface IRolePermissionMap'''
        r=[]
        for role, permissions in self._rp.items():
            if permission in permissions: r.append((role, Allow))
        return r

    def getPermissionAcquired(self, permission):
        '''See interface IRolePermissionMap'''
        return 1

    def getPermissionsForRole(self, role):
        '''See interface IRolePermissionMap'''
        return [(perm, Allow) for perm in self._rp[role]]

    def setPermissionAcquired(self, permission, flag):
        '''See interface IRolePermissionManager'''
        raise TypeError

    def unsetPermissionFromRole(self, permission, role):
        '''See interface IRolePermissionManager'''
        permissions = self._rp.get(role, ())
        if permission in permissions:
            permissions.remove(permission)
            if not permissions:
                # XXX: this del removed by Steve and Casey
                #      in order to get the PermissionsForRole
                #      view unit tests to work correctly.
                #
                #      Why is this del here?
                #
                #      It doesn't seem to break anything to remove
                #      it, like this!
                #del self._rp[role]
                pass


    def grantPermissionToRole(self, permission, role):
        '''See interface IRolePermissionManager'''
        if role in self._rp:
            if permission not in self._rp[role]:
                self._rp[role].append(permission)
        else:
            self._rp[role] = [permission]

