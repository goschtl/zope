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
"""
The objectpolicy package makes it easy to override the default
zope.securitypolicy.zopepolicy on an object by object basis.

By default all objects use the zopepolicy. Objects that want to have
their own policy should have a marker interface `IObjectPolicyMarker`
and have an adapter to `IObjectPolicy`.

"""

import zope.interface
import zope.component

from zope.securitypolicy.zopepolicy import ZopeSecurityPolicy
from zope.security.checker import CheckerPublic
from zope.security.proxy import removeSecurityProxy
from zope.security.management import system_user

from z3c.objectpolicy.interfaces import IObjectPolicyMarker
from z3c.objectpolicy.interfaces import IObjectPolicy

from zope.securitypolicy.interfaces import Allow, Deny, Unset

from zope.securitypolicy.interfaces import IPrincipalPermissionManager
from zope.securitypolicy.principalpermission import AnnotationPrincipalPermissionManager
from zope.securitypolicy.interfaces import IRolePermissionManager
from zope.securitypolicy.rolepermission import AnnotationRolePermissionManager


class ObjectPolicy(ZopeSecurityPolicy):

    def checkZopePermission(self, permission, object):
        return ZopeSecurityPolicy.checkPermission(self, permission, object)

    def checkPermission(self, permission, object):
        if permission is CheckerPublic:
            return True

        object = removeSecurityProxy(object)

        if IObjectPolicyMarker.providedBy(object):
            try:
                adapted = IObjectPolicy(object)
            except TypeError:
                return self.checkZopePermission(permission, object)

            return adapted.checkPermission(self, permission)
        else:
            return self.checkZopePermission(permission, object)

class ObjectPrincipalPermissionManager(AnnotationPrincipalPermissionManager):
    zope.component.adapts(IObjectPolicyMarker)
    zope.interface.implements(IPrincipalPermissionManager)

    def __init__(self, context):
        super(ObjectPrincipalPermissionManager, self).__init__(context)

        try:
            self._adapted = IObjectPolicy(context)
        except TypeError:
            self.getSetting = self.getZopePrincipalSetting

    def getPrincipalsForPermission(self, permission_id):
        """Get the principas that have a permission.

        Return the list of (principal_id, setting) tuples that describe
        security assertions for this permission.

        If no principals have been set for this permission, then the empty
        list is returned.
        """
        raise NotImplementedError("Seemed like nobody calls getPrincipalsForPermission")
        return super(ObjectPrincipalPermissionManager, self).getPrincipalsForPermission(
            permission_id)

    def getPermissionsForPrincipal(self, principal_id):
        """Get the permissions granted to a principal.

        Return the list of (permission, setting) tuples that describe
        security assertions for this principal.

        If no permissions have been set for this principal, then the empty
        list is returned.
        """
        raise NotImplementedError("Seemed like nobody calls getPermissionsForPrincipal")
        return super(ObjectPrincipalPermissionManager, self).getPermissionsForPrincipal(
            principal_id)

    def getZopePrincipalSetting(self, permission_id, principal_id, default=Unset):
        return super(ObjectPrincipalPermissionManager, self).getSetting(
            permission_id, principal_id, default)

    def getSetting(self, permission_id, principal_id, default=Unset):
        """Get the setting for a permission and principal.

        Get the setting (Allow/Deny/Unset) for a given permission and
        principal.
        """
        return self._adapted.getPrincipalPermission(
            self, permission_id, principal_id, default)

    def getPrincipalsAndPermissions(self):
        """Get all principal permission settings.

        Get the principal security assertions here in the form
        of a list of three tuple containing
        (permission id, principal id, setting)
        """
        raise NotImplementedError("Seemed like nobody calls getPrincipalsAndPermissions")
        return super(ObjectPrincipalPermissionManager, self).getPrincipalsAndPermissions()

    #def grantPermissionToPrincipal(self, permission_id, principal_id):
    #    """Assert that the permission is allowed for the principal.
    #    """
    #
    #def denyPermissionToPrincipal(self, permission_id, principal_id):
    #    """Assert that the permission is denied to the principal.
    #    """
    #
    #def unsetPermissionForPrincipal(self, permission_id, principal_id):
    #    """Remove the permission (either denied or allowed) from the
    #    principal.
    #    """

class ObjectRolePermissionManager(AnnotationRolePermissionManager):
    zope.component.adapts(IObjectPolicyMarker)
    zope.interface.implements(IRolePermissionManager)

    def __init__(self, context):
        super(ObjectRolePermissionManager, self).__init__(context)

        try:
            self._adapted = IObjectPolicy(context)
        except TypeError:
            self.getSetting = self.getZopeRoleSetting

    def getPermissionsForRole(self, role_id):
        """Get the premissions granted to a role.

        Return a sequence of (permission id, setting) tuples for the given
        role.

        If no permissions have been granted to this
        role, then the empty list is returned.
        """
        print "ROLE:getPermissionsForRole"
        return super(ObjectRolePermissionManager, self).getPermissionsForRole(
            role_id)

    def getRolesForPermission(permission_id):
        """Get the roles that have a permission.

        Return a sequence of (role id, setting) tuples for the given
        permission.

        If no roles have been granted this permission, then the empty list is
        returned.
        """
        print "ROLE:getRolesForPermission"
        return super(ObjectRolePermissionManager, self).getRolesForPermission(
            permission_id)

    def getZopeRoleSetting(self, permission_id, role_id):
        return super(ObjectRolePermissionManager, self).getSetting(
            permission_id, role_id)

    def getSetting(self, permission_id, role_id):
        """Return the setting for the given permission id and role id

        If there is no setting, Unset is returned
        """
        return self._adapted.getRolePermission(
            self, permission_id, role_id)

    def getRolesAndPermissions():
        """Return a sequence of (permission_id, role_id, setting) here.

        The settings are returned as a sequence of permission, role,
        setting tuples.

        If no principal/role assertions have been made here, then the empty
        list is returned.
        """
        print "ROLE:getRolesAndPermissions"
        return super(ObjectRolePermissionManager, self).getRolesAndPermissions()


    #def grantPermissionToRole(permission_id, role_id):
    #    """Bind the permission to the role.
    #    """
    #
    #def denyPermissionToRole(permission_id, role_id):
    #    """Deny the permission to the role
    #    """
    #
    #def unsetPermissionFromRole(permission_id, role_id):
    #    """Clear the setting of the permission to the role.
    #    """

class DefaultObjectPolicyAdapter(object):
    zope.interface.implements(IObjectPolicy)

    def __init__(self, context):
        self.context = context

    def getPrincipalPermission(self, manager, permissionid, principalid, default):
        #return the Z3 default permissions
        return manager.getZopePrincipalSetting(
            permissionid, principalid, default)

    def getRolePermission(self, manager, permissionid, roleid):
        #return the Z3 default permissions
        return manager.getZopeRoleSetting(
            permissionid, roleid)

    def checkPermission(self, manager, permissionid):
        #print permissionid, str(self.context)
        return manager.checkZopePermission(permissionid, self.context)

    def checkPermissionForParticipation(self, manager, permissionid):
        object = self.context
        seen = {}
        for participation in manager.participations:
            principal = participation.principal
            if principal is system_user:
                continue # always allow system_user

            if principal.id in seen:
                continue

            if not self.checkPermissionForParticipant(
                manager, principal, permissionid,
                ):
                return False

            seen[principal.id] = 1

        return True

    def checkPermissionForParticipant(self, manager, principal, permissionid):
        return manager.cached_decision(
                self.context, principal.id,
                manager._groupsFor(principal), permissionid,
                )
