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
"""Management view component for principal-role management (Zope2's
"local roles").

$Id: principalroleview.py,v 1.3 2004/01/15 23:25:22 stevea Exp $
"""
from datetime import datetime

from zope.app.i18n import ZopeMessageIDFactory as _
from zope.products.securitypolicy.interfaces import IPrincipalRoleManager
from zope.products.securitypolicy.interfaces import IPrincipalRoleMap
from zope.app.security.settings import Unset, Deny, Allow
from zope.app.services.servicenames import Authentication
from zope.component import getService, getAdapter

class PrincipalRoleView:

    def getAllPrincipals(self):
        principals = getattr(self, '_principals', None)
        if principals is None:
            principals = self._principals = getService(
                self.context, Authentication
                ).getPrincipals('')
        return principals

    def getAllRoles(self):
        roles = getattr(self, '_roles', None)
        if roles is None:
            roles = self._roles = getService(self.context, "Roles"
                ).getRoles()
        return roles

    def createGrid(self, principals=None, roles=None):
        if principals is None:
            principals = self.request.get('principals')
            if principals is None:
                principals = self.getAllPrincipals()
            else:
                # Ugh, we have ids, but we want objects
                auth_service = getService(self.context, Authentication)
                principals = [auth_service.getPrincipal(principal)
                              for principal in principals]


        if roles is None:
            roles = self.request.get('roles')
            if roles is None:
                roles = self.getAllRoles()
            else:
                # Ugh, we have ids, but we want objects
                # XXX This code path needs a test
                role_service = getService(self.context, 'Roles')
                roles = [role_service.getRole(role)
                         for role in roles]

        return PrincipalRoleGrid(principals, roles, self.context)

    def update(self, testing=None):
        status = ''

        if 'APPLY' in self.request:
            principals = self.request.get('principals')
            roles = self.request.get('roles')
            prm = getAdapter(self.context, IPrincipalRoleManager)
            for role in roles:
                for principal in principals:
                    name = 'grid.%s.%s' % (role, principal)
                    setting = self.request.get(name, 'Unset')
                    if setting == 'Unset':
                        prm.unsetRoleForPrincipal(role, principal)
                    elif setting == 'Allow':
                        prm.assignRoleToPrincipal(role, principal)
                    elif setting == 'Deny':
                        prm.removeRoleFromPrincipal(role, principal)
                    else:
                        raise ValueError("Incorrect setting %s" % setting)

            formatter = self.request.locale.getDateTimeFormatter('medium')
            status = _("Settings changed at ${date_time}")
            status.mapping = {'date_time': formatter.format(datetime.utcnow())}

        return status

class PrincipalRoleGrid:

    def __init__(self, principals, roles, context):
        self._principals = principals
        self._roles = roles
        self._grid = {}

        map = getAdapter(context, IPrincipalRoleMap)

        for role in roles:
            rid = role.getId()
            for principal in principals:
                pid = principal.getId()
                setting = map.getSetting(rid, pid)
                self._grid[(pid, rid)] = setting.getName()

    def principals(self):
        return self._principals

    def principalIds(self):
        return [p.getId() for p in self._principals]

    def roles(self):
        return self._roles

    def roleIds(self):
        return [r.getId() for r in self._roles]

    def getValue(self, principal_id, role_id):
        return self._grid[(principal_id, role_id)]

    def listAvailableValues(self):
        return (Unset.getName(), Allow.getName(), Deny.getName())
