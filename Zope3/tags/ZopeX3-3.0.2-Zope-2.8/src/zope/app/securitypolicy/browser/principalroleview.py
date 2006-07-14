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
"""Management view component for principal-role management (Zope2's
'local roles').

$Id$
"""
from datetime import datetime

from zope.app import zapi
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.security.settings import Unset, Deny, Allow
from zope.app.servicenames import Authentication

from zope.app.securitypolicy.interfaces import IRole
from zope.app.securitypolicy.interfaces import IPrincipalRoleManager
from zope.app.securitypolicy.interfaces import IPrincipalRoleMap

class PrincipalRoleView(object):

    def getAllPrincipals(self):
        principals = getattr(self, '_principals', None)
        if principals is None:
            auth = zapi.getService(Authentication)
            principals = self._principals = auth.getPrincipals('')
        return principals

    def getAllRoles(self):
        roles = getattr(self, '_roles', None)
        if roles is None:
            roles = self._roles = \
              [role
               for name, role in zapi.getUtilitiesFor(IRole)]
        return roles

    def createGrid(self, principals=None, roles=None):
        if principals is None:
            principals = self.request.get('principals')
            if principals is None:
                principals = self.getAllPrincipals()
            else:
                # Ugh, we have ids, but we want objects
                auth_service = zapi.getService(Authentication)
                principals = [auth_service.getPrincipal(principal)
                              for principal in principals]


        if roles is None:
            roles = self.request.get('roles')
            if roles is None:
                roles = self.getAllRoles()
            else:
                # XXX This code path needs a test
                utils = zapi.getUtilitiesFor(IRole)
                roles = [role for name, role in utils if name in roles]

        return PrincipalRoleGrid(principals, roles, self.context)

    def update(self, testing=None):
        status = ''

        if 'APPLY' in self.request:
            principals = self.request.get('principals')
            roles = self.request.get('roles')
            prm = IPrincipalRoleManager(self.context)
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

            formatter = self.request.locale.dates.getFormatter(
                'dateTime', 'medium')
            status = _("Settings changed at ${date_time}")
            status.mapping = {'date_time': formatter.format(datetime.utcnow())}

        return status

class PrincipalRoleGrid(object):

    def __init__(self, principals, roles, context):
        self._principals = principals
        self._roles = roles
        self._grid = {}

        map = IPrincipalRoleMap(context)

        for role in roles:
            rid = role.id
            for principal in principals:
                pid = principal.id
                setting = map.getSetting(rid, pid)
                self._grid[(pid, rid)] = setting.getName()

    def principals(self):
        return self._principals

    def principalIds(self):
        return [p.id for p in self._principals]

    def roles(self):
        return self._roles

    def roleIds(self):
        return [r.id for r in self._roles]

    def getValue(self, principal_id, role_id):
        return self._grid[(principal_id, role_id)]

    def listAvailableValues(self):
        return (Unset.getName(), Allow.getName(), Deny.getName())
