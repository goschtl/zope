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

$Id$
"""
from datetime import datetime

from zope.app import zapi
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.security.settings import Unset, Allow, Deny
from zope.app.security.interfaces import IPermission

from zope.app.securitypolicy.interfaces import IRole, IRolePermissionManager
from zope.app.securitypolicy.permissionroles import PermissionRoles
from zope.app.securitypolicy.rolepermission import RolePermissions

class RolePermissionView:

    def roles(self):
        roles = getattr(self, '_roles', None)
        if roles is None:
            roles = self._roles = \
              [role for name, role in zapi.getUtilitiesFor(IRole)]
        return roles

    def permissions(self):
        permissions = getattr(self, '_permissions', None)
        if permissions is None:
            permissions = self._permissions = \
              [perm for name, perm in zapi.getUtilitiesFor(IPermission)]
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
        roles = self.roles()
        perm = zapi.getUtility(IPermission, pid)
        return PermissionRoles(perm, self.context, roles)

    def roleForID(self, rid):
        permissions = self.permissions()
        role = zapi.getUtility(IRole, rid)
        return RolePermissions(role, self.context, permissions)


    def update(self, testing=None):
        status = ''
        changed = False

        if 'SUBMIT' in self.request:
            roles       = [r.id for r in self.roles()]
            permissions = [p.id for p in self.permissions()]
            prm         = IRolePermissionManager(self.context)
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
            prm = IRolePermissionManager(self.context)
            roles = self.roles()
            rperm = self.request.get('permission_id')
            settings = self.request.get('settings', ())
            for ir in range(len(roles)):
                rrole = roles[ir].id
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
            prm = IRolePermissionManager(self.context)
            allowed = self.request.get(Allow.getName(), ())
            denied = self.request.get(Deny.getName(), ())
            for permission in self.permissions():
                rperm = permission.id
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
            formatter = self.request.locale.dates.getFormatter(
                'dateTime', 'medium')
            status = _("Settings changed at ${date_time}")
            status.mapping = {'date_time': formatter.format(datetime.utcnow())}

        return status

