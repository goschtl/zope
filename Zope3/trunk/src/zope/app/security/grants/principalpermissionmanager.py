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
"""Mappings between principals and permissions."""

from zope.app.interfaces.security \
     import IPrincipalPermissionManager
from zope.app.security.grants.localsecuritymap import LocalSecurityMap
from zope.app.security.settings import Allow, Deny, Unset


class PrincipalPermissionManager(LocalSecurityMap):
    """Mappings between principals and permissions."""

    __implements__ = IPrincipalPermissionManager

    def grantPermissionToPrincipal( self, permission_id, principal_id ):
        ''' See the interface IPrincipalPermissionManager '''
        self.addCell( permission_id, principal_id, Allow )

    def denyPermissionToPrincipal( self, permission_id, principal_id ):
        ''' See the interface IPrincipalPermissionManager '''
        self.addCell( permission_id, principal_id, Deny )

    def unsetPermissionForPrincipal( self, permission_id, principal_id ):
        ''' See the interface IPrincipalPermissionManager '''
        self.delCell( permission_id, principal_id )

    def getPrincipalsForPermission( self, permission_id ):
        ''' See the interface IPrincipalPermissionManager '''
        return self.getRow( permission_id )

    def getPermissionsForPrincipal( self, principal_id ):
        ''' See the interface IPrincipalPermissionManager '''
        return self.getCol( principal_id )

    def getSetting( self, permission_id, principal_id ):
        ''' See the interface IPrincipalPermissionManager '''
        return self.getCell( permission_id, principal_id, default=Unset )

    def getPrincipalsAndPermissions( self ):
        ''' See the interface IPrincipalPermissionManager '''
        return self.getAllCells()


# Permissions are our rows, and principals are our columns
principalPermissionManager = PrincipalPermissionManager()


# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from zope.testing.cleanup import addCleanUp
addCleanUp(principalPermissionManager._clear)
del addCleanUp
