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
"""Role Permission View Classes

$Id: rolepermissionview.py,v 1.2 2004/01/14 22:55:33 chrism Exp $
"""
from datetime import datetime

from zope.app.i18n import ZopeMessageIDFactory as _
from zope.products.securitypolicy.interfaces import IRolePermissionManager
from zope.products.securitypolicy.permissionroles import PermissionRoles
from zope.products.securitypolicy.rolepermission import RolePermissions
from zope.app.security.settings import Unset, Allow, Deny
from zope.app.services.servicenames import Permissions
from zope.component import getService, getAdapter

class RolePermissionView:

    def roles(self):
        roles = getattr(self, '_roles', None)
        if roles is None:
            roles = self._roles = getService(
                self.context, "Roles"
                ).getRoles()
        return roles

    def permissions(self):
        permissions = getattr(self, '_permissions', None)
        if permissions is None:
            permissions = self._permissions = getService(
                self.context, Permissions
                ).getPermissions()
        return permissions

    def availableSettings(self, noacquire=False):
        aq = {'id': Unset.getName(), 'shorttitle': ' ',
              'title': _('permission-acquire', 'Acquire')}
        rest = [{'id': Allow.getName(), 'shorttitle': '+',
                 'title': _('permission-allow', 'Allow')},
                {'id': Deny.getName(), 'shorttitle': '-',
                 'title': _('permission-deny', 'Deny')},
                ]
        if noacquire:
            return rest
        else:
            return [aq]+rest

    def permissionRoles(self):
        context = self.context
        roles = self.roles()
        return [PermissionRoles(permission, context, roles)
                for permission in self.permissions()]

    def permissionForID(self, pid):
        context = self.context
        roles = self.roles()
        perm = getService(context, Permissions
                          ).getPermission(pid)
        return PermissionRoles(perm, context, roles)

    def roleForID(self, rid):
        context = self.context
        permissions = self.permissions()
        role = getService(context, "Roles"
                          ).getRole(rid)
        return RolePermissions(role, context, permissions)


    def update(self, testing=None):
        status = ''
        changed = False

        if 'SUBMIT' in self.request:
            roles       = [r.getId() for r in self.roles()]
            permissions = [p.getId() for p in self.permissions()]
            prm         = getAdapter(self.context, IRolePermissionManager)
            for ip in range(len(permissions)):
                rperm = self.request.get("p%s" % ip)
                if rperm not in permissions: continue
                for ir in range(len(roles)):
                    rrole = self.request.get("r%s" % ir)
                    if rrole not in roles: continue
                    setting = self.request.get("p%sr%s" % (ip, ir), None)
                    if setting is not None:
                        if setting == Unset.getName():
                            prm.unsetPermissionFromRole(rperm, rrole)
                        elif setting == Allow.getName():
                            prm.grantPermissionToRole(rperm, rrole)
                        elif setting == Deny.getName():
                            prm.denyPermissionToRole(rperm, rrole)
                        else:
                            raise ValueError("Incorrect setting: %s" % setting)
            changed = True

        if 'SUBMIT_PERMS' in self.request:
            prm = getAdapter(self.context, IRolePermissionManager)
            roles = self.roles()
            rperm = self.request.get('permission_id')
            settings = self.request.get('settings', ())
            for ir in range(len(roles)):
                rrole = roles[ir].getId()
                setting = settings[ir]
                if setting == Unset.getName():
                    prm.unsetPermissionFromRole(rperm, rrole)
                elif setting == Allow.getName():
                    prm.grantPermissionToRole(rperm, rrole)
                elif setting == Deny.getName():
                    prm.denyPermissionToRole(rperm, rrole)
                else:
                    raise ValueError("Incorrect setting: %s" % setting)
            changed = True

        if 'SUBMIT_ROLE' in self.request:
            role_id = self.request.get('role_id')
            prm = getAdapter(self.context, IRolePermissionManager)
            allowed = self.request.get(Allow.getName(), ())
            denied = self.request.get(Deny.getName(), ())
            for permission in self.permissions():
                rperm = permission.getId()
                if rperm in allowed and rperm in denied:
                    raise ValueError("Incorrect setting for %s" % rperm)
                if rperm in allowed:
                    prm.grantPermissionToRole(rperm, role_id)
                elif rperm in denied:
                    prm.denyPermissionToRole(rperm, role_id)
                else:
                    prm.unsetPermissionFromRole(rperm, role_id)
            changed = True

        if changed:
            formatter = self.request.locale.getDateTimeFormatter('medium')
            status = _("Settings changed at ${date_time}")
            status.mapping = {'date_time': formatter.format(datetime.utcnow())}

        return status

