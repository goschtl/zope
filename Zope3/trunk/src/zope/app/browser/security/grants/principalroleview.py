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
""" Management view component for principal-role management (Zope2's
    "local roles").

$Id: principalroleview.py,v 1.4 2003/02/11 15:59:35 sidnei Exp $
"""
import time

from zope.app.interfaces.security import IPermission
from zope.app.interfaces.security import IPrincipalRoleManager
from zope.app.interfaces.security import IPrincipalRoleMap
from zope.app.interfaces.security import IRole
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.security.settings import Unset, Deny, Allow
from zope.component import getService, getAdapter
from zope.component.contextdependent import ContextDependent
from zope.component.servicenames import Authentication, Roles
from zope.publisher.browser import BrowserView


class PrincipalRoleView(BrowserView):

    index = ViewPageTemplateFile('principal_role_association.pt')

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
            roles = self._roles = getService(self.context, Roles
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
                role_service = getService(self.context, Roles)
                roles = [role_service.getRole(role)
                         for role in roles]

        return PrincipalRoleGrid(principals, roles, self.context)

    def action(self, principals, roles, testing=None):
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

        if not testing:
            return self.index(
                message="Settings changed at %s" % time.ctime(time.time())
                )


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
