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

$Id: RolePermissionView.py,v 1.1 2002/06/20 15:55:00 jim Exp $
"""

import time
from Zope.App.PageTemplate import ViewPageTemplateFile
from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.ComponentArchitecture import getService, getAdapter
from Zope.App.Security.IRolePermissionManager import IRolePermissionManager
from Zope.App.Security.Grants.PermissionRoles import PermissionRoles
from Zope.App.Security.Grants.RolePermissions import RolePermissions


class RolePermissionView(BrowserView):

    index = ViewPageTemplateFile('manage_access.pt')
    manage_permissionForm = ViewPageTemplateFile('manage_permissionForm.pt')
    manage_roleForm = ViewPageTemplateFile('manage_roleForm.pt')
    
    def roles(self):
        roles = getattr(self, '_roles', None)
        if roles is None:
            roles = self._roles = getService(
                self.context, 'RoleService'
                ).getRoles()
        return roles

    def permissions(self):
        permissions = getattr(self, '_permissions', None)
        if permissions is None:
            permissions = self._permissions = getService(
                self.context, 'PermissionService'
                ).getPermissions()
        return permissions

        
    def permissionRoles(self):
        context = self.context
        roles = self.roles()
        return [PermissionRoles(permission, context, roles)
                for permission in self.permissions()]

    def permissionForID(self, pid):
        context = self.context
        roles = self.roles()
        perm = getService(context, 'PermissionService'
                          ).getPermission(pid)
        return PermissionRoles(perm, context, roles)

    def roleForID(self, rid):
        context = self.context
        permissions = self.permissions()
        role = getService(context, 'RoleService'
                          ).getRole(rid)
        return RolePermissions(role, context, permissions)


    def action(self, REQUEST, testing=None):
        roles       = [r.getId() for r in self.roles()]
        permissions = [p.getId() for p in self.permissions()]
        prm         = getAdapter(self.context, IRolePermissionManager)
        for ip in range(len(permissions)):
            rperm = REQUEST.get("p%s" % ip)
            if rperm not in permissions: continue
            for ir in range(len(roles)):
                rrole = REQUEST.get("r%s" % ir)
                if rrole not in roles: continue
                if ("p%sr%s" % (ip, ir))  in REQUEST:
                    prm.grantPermissionToRole(rperm, rrole)
                else:
                    prm.unsetPermissionFromRole(rperm, rrole)

        if not testing:
            return self.index( REQUEST,
                message="Settings changed at %s" % time.ctime(time.time())
                )

    def update_permission(self, REQUEST, permission_id,
                          roles=(), testing=None):
        prm = getAdapter(self.context, IRolePermissionManager)

        for ir in [r.getId() for r in self.roles()]:
            if ir in roles:
                prm.grantPermissionToRole(permission_id, ir)
            else:
                prm.unsetPermissionFromRole(permission_id, ir)
        if not testing:
            return self.index(REQUEST,
                              message="Settings changed at %s"
                                  % time.ctime(time.time())
                              )

    def update_role(self, REQUEST, role_id,
                    permissions=(), testing=None):
        prm = getAdapter(self.context, IRolePermissionManager)

        for ip in [p.getId() for p in self.permissions()]:
            if ip in permissions:
                prm.grantPermissionToRole(ip, role_id)
            else:
                prm.unsetPermissionFromRole(ip, role_id)
        if not testing:
            return self.index(REQUEST,
                              message="Settings changed at %s"
                                  % time.ctime(time.time())
                              )        
        
    
