##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Principal Permission View Classes

$Id$
"""
import time

from zope.app.publisher.browser import BrowserView

from zope.app import zapi
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.servicenames import Authentication
from zope.app.security.interfaces import IPermission
from zope.app.security.settings import Allow, Deny, Unset

from zope.app.securitypolicy.interfaces import IPrincipalPermissionManager
from zope.app.securitypolicy.interfaces import IPrincipalPermissionMap


class PrincipalPermissionView(BrowserView):

    index = ViewPageTemplateFile('principal_permission_edit.pt')

    def get_principal(self, principal_id):
        return zapi.getService(Authentication).getPrincipal(principal_id)

    def unsetPermissions(self, principal_id, permission_ids, REQUEST=None):
        """Form action unsetting a principals permissions"""
        principal = self.get_principal(principal_id)
        ppm = IPrincipalPermissionManager(self.context)

        for perm_id in permission_ids:
            permission = zapi.getUtility(IPermission, perm_id)
            ppm.unsetPermissionForPrincipal(permission , principal)

        if REQUEST is not None:
            return self.index(message="Settings changed at %s"
                                        % time.ctime(time.time()))

    def grantPermissions(self, principal_id, permission_ids, REQUEST=None):
        """Form action granting a list of permissions to a principal"""
        principal = self.get_principal(principal_id)
        ppm = IPrincipalPermissionManager(self.context)

        for perm_id in permission_ids:
            permission = zapi.getUtility(IPermission, perm_id)
            ppm.grantPermissionToPrincipal(permission , principal)
        if REQUEST is not None:
            return self.index(message="Settings changed at %s"
                                        % time.ctime(time.time()))

    def denyPermissions(self, principal_id, permission_ids, REQUEST=None):
        """Form action denying a list of permissions for a principal"""
        principal = self.get_principal(principal_id)
        ppm = IPrincipalPermissionManager(self.context)

        for perm_id in permission_ids:
            permission = zapi.getUtility(IPermission, perm_id)
            ppm.denyPermissionToPrincipal(permission , principal)
        if REQUEST is not None:
            return self.index(message="Settings changed at %s"
                                        % time.ctime(time.time()))

    # Methods only called from the zpt view
    def getUnsetPermissionsForPrincipal(self, principal_id):
        """Returns all unset permissions for this principal"""
        ppmap = IPrincipalPermissionMap(self.context)
        principal = self.get_principal(principal_id)
        result = []
        for perm in zapi.getUtilitiesFor(IPermission):
            if ppmap.getSetting(perm, principal) == Unset:
                result.append(perm)

        return result

    def getPermissionsForPrincipal(self, principal_id, setting_name):
        """Return a list of permissions with the given setting_name
           string for the principal.

           Return empty list if there are no permissions.
        """

        ppmap = IPrincipalPermissionMap(self.context)
        principal = self.get_principal(principal_id)

        permission_settings = ppmap.getPermissionsForPrincipal(principal)
        setting_map = {'Deny': Deny, 'Allow':Allow}
        asked_setting = setting_map[setting_name]

        result = []
        for permission, setting in permission_settings:
            if asked_setting == setting:
                result.append(permission)

        return result
