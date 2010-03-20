##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from zope.interface import Interface

class IObjectPolicyMarker(Interface):
    """Marker interface to mark objects wanting their own security policy"""

class IObjectPolicy(Interface):
    """ """
    def getPrincipalPermission(self, manager, permissionid, principalid, default):
        """Return whether security policy allows permission
        on the context object to the principal.

        Arguments:
        manager -- The default Z3 AnnotationPrincipalPermissionManager
                   which gets the permission from the annotations
        permissionid -- A permission ID
        principalid -- A principal ID (participation.principal.id)
        default -- The default value proposed by AnnotationPrincipalPermissionManager

        return:
        one of zope.app.securitypolicy.interfaces.[Allow, Deny, Unset]
        """

    def getRolePermission(self, manager, permissionid, roleid):
        """Return whether security policy allows permission
        on the context object to the role.

        Arguments:
        manager -- The default Z3 AnnotationRolePermissionManager
                   which gets the permission from the annotations
        permissionid -- A permission ID
        roleid -- A role ID (determined by ZopeSecurityPolicy)

        return:
        one of zope.app.securitypolicy.interfaces.[Allow, Deny, Unset]
        """

    def checkPermission(manager, permissionid):
        """Return whether security policy allows permission
        on the context object.

        manager -- The default Z3 ZopePolicy,
                   which can be used to get default permissions
        permissionid -- A permission ID

        The method should go through manager.participations.principal's
        to check permissions, see checkPermissionForParticipation

        return:
        True -- access granted
        False -- no access
        """

    def checkPermissionForParticipation(manager, permissionid):
        """Go thrugh manager.participations.principal's
        call self.checkPermissionForParticipant for each one
        convinience method

        return:
        True -- access granted
        False -- no access
        """

    def checkPermissionForParticipant(self, manager, principal, permissionid):
        """Called by checkPermissionForParticipation for each principal

        manager -- The default Z3 ZopePolicy,
                   which can be used to get default permissions
        principal -- A principal
        permissionid -- A permission ID

        return:
        True -- access granted
        False -- no access
        """