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
from IRoleManagement import IRoleManagement
from IZope3RoleManageable import IZope3RoleManageable
from IZope3RoleManageable import SPECIAL_ATTRIBUTE_NAME

class _PermissionRoleBindings:
    def __init__( self ):
        self._permissions = {}
        self._roles = {}

class Zope3RoleManagement:
    """
        Implement IRoleManagement for new-style objects.
    """

    __implements__ = (IRoleManagement, )

    def __init__(self, context):
        self.context = context


    def _getContextBindings( self ):
        """
            Find or create the permission-role bindings for our context.
        """
        bindings = getattr( self.context, SPECIAL_ATTRIBUTE_NAME, None )

        if bindings is None:
            bindings = _PermissionRoleBindings()
            setattr( self.context, SPECIAL_ATTRIBUTE_NAME, bindings )

        return bindings

    #
    #   IRoleManagement implementation
    #
    def listAvailableRoles( self ):
        """
            What roles are available at our context?
        """
        roles = self._getContextBindings()._roles
        return tuple( roles.keys() )

    def addRole( self, role_name ):
        """
            Create a new, empty role.
        """
        roles = self._getContextBindings()._roles

        if role_name in roles:
            raise KeyError, 'Role %s already defined.' % role_name

        roles[ role_name ] = ()

    def removeRole( self, role_name ):
        """
            Remove a role, and any associated permission bindings.
        """
        roles = self._getContextBindings()._roles

        if not (role_name in roles):
            raise KeyError, 'Role %s not defined.' % role_name

        self.clearPermissionsOfRole( role_name )
        del roles[ role_name ]

    def listPermissionsOfRole( self, role_name ):
        """
            What permissions does the 'role_name' have?
        """

    def clearPermissionsOfRole( self, role_name ):
        """
            Remove all permissions from 'role_name'.
        """

    def addPermissionToRole( self, role_name, permission ):
        """
            Add 'permission' to 'role_name'.
        """

    def listRolesWithPermission( self, permission ):
        """
            Which roles have 'permission' in our context?
        """
