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
"""

$Id: principalpermissionview.py,v 1.5 2003/02/12 02:17:09 seanb Exp $
"""
import time

from zope.app.interfaces.security import IPrincipalPermissionManager
from zope.app.interfaces.security import IPrincipalPermissionMap
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.security.settings import Allow, Deny, Unset
from zope.component import getService, getAdapter
from zope.app.services.servicenames import Permissions, Authentication
from zope.publisher.browser import BrowserView


class PrincipalPermissionView(BrowserView):

    index = ViewPageTemplateFile('pt/principal_permission_edit.pt')

    def get_permission_service(self):
        return getService(self.context, Permissions)

    def get_principal(self, principal_id):
        return getService(self.context,
                          Authentication
                          ).getPrincipal(principal_id)

    def unsetPermissions(self, principal_id, permission_ids, REQUEST=None):
        """Form action unsetting a principals permissions"""
        permission_service = self.get_permission_service()
        principal = self.get_principal(principal_id)
        ppm = getAdapter(self.context, IPrincipalPermissionManager)

        for perm_id in permission_ids:
            permission = permission_service.getPermission(perm_id)
            ppm.unsetPermissionForPrincipal(permission , principal)

        if REQUEST is not None:
            return self.index(message="Settings changed at %s"
                                        % time.ctime(time.time()))

    def grantPermissions(self, principal_id, permission_ids, REQUEST=None):
        """Form action granting a list of permissions to a principal"""
        permission_service = self.get_permission_service()
        principal = self.get_principal(principal_id)
        ppm = getAdapter(self.context, IPrincipalPermissionManager)

        for perm_id in permission_ids:
            permission = permission_service.getPermission(perm_id)
            ppm.grantPermissionToPrincipal(permission , principal)
        if REQUEST is not None:
            return self.index(message="Settings changed at %s"
                                        % time.ctime(time.time()))

    def denyPermissions(self, principal_id, permission_ids, REQUEST=None):
        """Form action denying a list of permissions for a principal"""
        permission_service = self.get_permission_service()
        principal = self.get_principal(principal_id)
        ppm = getAdapter(self.context, IPrincipalPermissionManager)

        for perm_id in permission_ids:
            permission = permission_service.getPermission(perm_id)
            ppm.denyPermissionToPrincipal(permission , principal)
        if REQUEST is not None:
            return self.index(message="Settings changed at %s"
                                        % time.ctime(time.time()))

    # Methods only called from the zpt view
    def getUnsetPermissionsForPrincipal(self, principal_id):
        """Returns all unset permissions for this principal"""

        ppmap = getAdapter(self.context, IPrincipalPermissionMap)
        principal = self.get_principal(principal_id)
        perm_serv = getService(self.context, Permissions)
        result = []
        for perm in perm_serv.getPermissions():
            if ppmap.getSetting(perm, principal) == Unset:
                result.append(perm)

        return result

    def getPermissionsForPrincipal(self, principal_id, setting_name):
        """Return a list of permissions with the given setting_name
           string for the principal.

           Return empty list if there are no permissions.
        """

        ppmap = getAdapter(self.context, IPrincipalPermissionMap)
        principal = self.get_principal(principal_id)

        permission_settings = ppmap.getPermissionsForPrincipal(principal)
        setting_map = {'Deny': Deny, 'Allow':Allow}
        asked_setting = setting_map[setting_name]

        result = []
        for permission, setting in permission_settings:
            if asked_setting == setting:
                result.append(permission)

        return result
