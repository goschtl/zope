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
"""Query interface for mappings between principals and permissions."""


from Interface import Interface

class IPrincipalPermissionMap(Interface):
    """Mappings between principals and permissions."""

    def getPrincipalsForPermission(permission_id):
        """Get the principas that have a permission.

        Return the list of (principal_id, setting) tuples that describe
        security assertions for this permission.

        If no principals have been set for this permission, then the empty
        list is returned. 
        """

    def getPermissionsForPrincipal(principal_id):
        """Get the permissions granted to a principal.

        Return the list of (permission, setting) tuples that describe
        security assertions for this principal.

        If no permissions have been set for this principal, then the empty
        list is returned. 
        """
        
    def getSetting(permission_id, principal_id): 
        """Get the setting for a permission and principal.

        Get the setting (Allow/Deny/Unset) for a given permission and
        principal. 
        """

    def getPrincipalsAndPermissions():
        """Get all principal permission settings.

        Get the principal security assertions here in the form
        of a list of three tuple containing 
        (permission id, principal id, setting)
        """



