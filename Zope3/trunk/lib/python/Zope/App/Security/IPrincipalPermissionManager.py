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
"""Management interface for mappings between principals and permissions."""

from Zope.App.Security.IPrincipalPermissionMap import IPrincipalPermissionMap


class IPrincipalPermissionManager(IPrincipalPermissionMap):
    """Management interface for mappings between principals and permissions."""

    def grantPermissionToPrincipal(permission_id, principal_id):
        """Assert that the permission is allowed for the principal.
        """

    def denyPermissionToPrincipal(permission_id, principal_id):
        """Assert that the permission is denied to the principal.
        """

    def unsetPermissionForPrincipal(permission_id, principal_id):
        """Remove the permission (either denied or allowed) from the
        principal.
        """
