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
"""Query interface for mappings between principals and roles."""


from Interface import Interface

class IPrincipalRoleMap(Interface):
    """Mappings between principals and roles."""

    def getPrincipalsForRole(role_id):
        """Return the list of (principal, setting) who have been assigned or 
        removed from a role.

        If no principals have been assigned this role,
        then the empty list is returned.
        """

    def getRolesForPrincipal(principal_id):
        """Return the list of (role, setting) assigned or removed from 
        this principal.

        If no roles have been assigned to
        this principal, then the empty list is returned.
        """

    def getSetting(role_id, principal_id):
        """Return the setting for this principal, role combination
        """

    def getPrincipalsAndRoles():
        """Return all the principal/role combinations along with the
        setting for each combination.
        """
        
