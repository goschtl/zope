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
"""Query interface for mappings between roles and permissions."""


from Interface import Interface


class IRolePermissionMap(Interface):
    """Mappings between roles and permissions."""

    def getPermissionsForRole(role_id):
        """Return a sequence of (permission id, setting) tuples for the given
        role.

        If no permissions have been granted to this
        role, then the empty list is returned.
        """

    def getRolesForPermission(permission_id):
        """Return a sequence of (role id, setting) tuples for the given
        permission.

        If no roles have been granted this permission, then the empty list is
        returned.  
        """

    def getSetting(permission_id, role_id):
        """Return the setting for the given permission id and role id

        If there is no setting, Unset is returned
        """

    def getPrincipalsAndRoles():
        """Return a sequence of (principal_id, role_id, setting) here.

        If no principal/role assertions have been made here, then the empty 
        list is returned.
        """
