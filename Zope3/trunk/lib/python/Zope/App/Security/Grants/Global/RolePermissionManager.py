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
"""Mappings between roles and permissions."""

from Zope.App.Security.Grants.LocalSecurityMap import LocalSecurityMap
from Zope.App.Security.Settings import Allow, Deny
from Zope.App.Security.IRolePermissionManager import IRolePermissionManager


class RolePermissionManager(LocalSecurityMap):
    """Mappings between roles and permissions."""

    __implements__ = IRolePermissionManager

    # Implementation methods for interface
    # Zope.App.Security.IRolePermissionManager

    def grantPermissionToRole( self, permission_id, role_id ):
        '''See interface IRolePermissionMap'''
        self.addCell( permission_id, role_id, Allow )

    def denyPermissionToRole( self, permission_id, role_id ):
        '''See interface IRolePermissionMap'''
        self.addCell( permission_id, role_id, Deny )

    def unsetPermissionFromRole( self, permission_id, role_id ):
        '''See interface IRolePermissionMap'''
        self.delCell( permission_id, role_id )

    def getRolesForPermission( self, permission_id ):
        '''See interface IRolePermissionMap'''
        return self.getRow( permission_id )

    def getPermissionsForRole( self, role_id ):
        '''See interface IRolePermissionMap'''
        return self.getCol( role_id )

    def getSetting( self, permission_id, role_id ):
        '''See interface IRolePermissionMap'''
        return self.getCell( permission_id, role_id )

    def getRolesAndPermissions( self ):
        '''See interface IRolePermissionMap'''
        return self.getAllCells()

# Permissions are our rows, and roles are our columns
rolePermissionManager = RolePermissionManager()

# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from Zope.Testing.CleanUp import addCleanUp
addCleanUp(rolePermissionManager._clear)
del addCleanUp
