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
"""Mappings between principals and roles."""

from Zope.App.Security.LocalSecurityMap import LocalSecurityMap
from Zope.App.Security.Settings import Assign, Remove, Unset
from Zope.App.Security.IPrincipalRoleManager import IPrincipalRoleManager
from Zope.App.Security.IPrincipalRoleMap import IPrincipalRoleMap



class PrincipalRoleManager(LocalSecurityMap):
    """Mappings between principals and roles."""

    __implements__ = ( IPrincipalRoleManager, IPrincipalRoleMap )

    def assignRoleToPrincipal( self, role_id, principal_id ):
        ''' See the interface IPrincipalRoleManager '''
        self.addCell( role_id, principal_id, Assign )

    def removeRoleFromPrincipal( self, role_id, principal_id ):
        ''' See the interface IPrincipalRoleManager '''
        self.addCell( role_id, principal_id, Remove )

    def unsetRoleForPrincipal( self, role_id, principal_id ):
        ''' See the interface IPrincipalRoleManager '''
        self.delCell( role_id, principal_id )

    def getPrincipalsForRole( self, role_id ):
        ''' See the interface IPrincipalRoleMap '''
        return self.getRow( role_id )

    def getRolesForPrincipal( self, principal_id ):
        ''' See the interface IPrincipalRoleMap '''
        return self.getCol( principal_id )

    def getSetting( self, role_id, principal_id ):
        ''' See the interface IPrincipalRoleMap '''
        return self.getCell( role_id, principal_id, default=Unset )

    def getPrincipalsAndRoles( self ):
        ''' See the interface IPrincipalRoleMap '''
        return self.getAllCells()

# Roles are our rows, and principals are our columns
principalRoleManager = PrincipalRoleManager()

# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from Zope.Testing.CleanUp import addCleanUp
addCleanUp(principalRoleManager._clear)
del addCleanUp
