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
"""Test IRolePermissionManager class that has no context.

$Id: RolePermissionManager.py,v 1.2 2002/06/24 16:00:44 efge Exp $
"""

from Zope.ComponentArchitecture import getAdapter
from Zope.App.Security.IRolePermissionManager import IRolePermissionManager
from Zope.App.Security.IRolePermissionMap import IRolePermissionMap
from Zope.App.Security.Grants.LocalSecurityMap import LocalSecurityMap
from Zope.App.Security.Settings import Allow, Deny, Unset

class RolePermissionManager:
    """
    provide adapter that manages role permission data in an object attribute
    """

    __implements__ = IRolePermissionManager, IRolePermissionMap

    def __init__(self):
        self._rp = LocalSecurityMap()

    def grantPermissionToRole(self, permission_id, role_id):
        ''' See the interface IRolePermissionManager '''
        rp = self._getRolePermissions(create=1)
        rp.addCell(permission_id, role_id, Allow)

    def denyPermissionToRole(self, permission_id, role_id):
        ''' See the interface IRolePermissionManager '''
        rp = self._getRolePermissions(create=1)
        rp.addCell(permission_id, role_id, Deny)

    def unsetPermissionFromRole(self, permission_id, role_id):
        ''' See the interface IRolePermissionManager '''
        rp = self._getRolePermissions()
        # Only unset if there is a security map, otherwise, we're done
        if rp:
            rp.delCell(permission_id, role_id)

    def getRolesForPermission(self, permission_id):
        '''See interface IRolePermissionMap'''
        rp = self._getRolePermissions()
        if rp:
            return rp.getRow(permission_id)
        else:
            return []

    def getPermissionsForRole(self, role_id):
        '''See interface IRolePermissionMap'''
        rp = self._getRolePermissions()
        if rp:
            return rp.getCol(role_id)
        else:
            return []

    def getRolesAndPermissions(self):
        '''See interface IRolePermissionMap'''
        rp = self._getRolePermissions()
        if rp:
            return rp.getAllCells(role_id)
        else:
            return []

    def getSetting(self, permission_id, role_id):
        '''See interface IRolePermissionMap'''
        rp = self._getRolePermissions()
        if rp:
            return rp.getCell(permission_id, role_id)
        else:
            return Unset

    def _getRolePermissions(self, create=0):
        """Get the role permission map stored in the context, optionally
           creating one if necessary"""
        return self._rp


