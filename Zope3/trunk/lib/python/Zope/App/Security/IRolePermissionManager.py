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
"""Management interface for mappings between roles and permissions."""

from Zope.App.Security.IRolePermissionMap import IRolePermissionMap


class IRolePermissionManager(IRolePermissionMap):
    """Management interface for mappings between roles and permissions."""

    def grantPermissionToRole(permission_id, role_id):
        """Bind the permission to the role.
        """

    def denyPermissionToRole(permission_id, role_id):
        """Deny the permission to the role
        """

    def unsetPermissionFromRole(permission_id, role_id):
        """Clear the setting of the permission to the role.
        """
