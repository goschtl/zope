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

$Id: PrincipalRoleView.py,v 1.3 2002/07/02 19:48:39 jim Exp $
"""

import time
from Zope.App.PageTemplate import ViewPageTemplateFile
from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.ComponentArchitecture.ContextDependent import ContextDependent
from Zope.ComponentArchitecture import getService, getAdapter

from Zope.App.Security.IPrincipalRoleManager import IPrincipalRoleManager
from Zope.App.Security.IPrincipalRoleMap import IPrincipalRoleMap

from Zope.App.Security.IPermission import IPermission
from Zope.App.Security.IRole import IRole

from Zope.App.Security.Settings import Unset


class PrincipalRoleView(BrowserView):

    index = ViewPageTemplateFile('principal_role_association.pt')

    def getAllPrincipals(self):
        principals = getattr(self, '_principals', None)
        if principals is None:
            principals = self._principals = getService(
                self.context, 'AuthenticationService'
                ).getPrincipals('')
            principals = [p.getId() for p in principals]
        return principals

    def getAllRoles(self):
        roles = getattr(self, '_roles', None)
        if roles is None:
            roles = self._roles = getService(self.context, 'RoleService'
                ).getRoles()
            roles = [r.getId() for r in roles]
        return roles

    def createGrid(self, principals=None, roles=None):
        if not principals:
            principals = self.getAllPrincipals()
        if not roles:
            roles = self.getAllRoles()
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
            for principal in principals:
                setting = map.getSetting(role, principal)
                self._grid[(principal, role)] = setting.getName()

    def principals(self):
        return self._principals

    def roles(self):
        return self._roles

    def getValue(self, principal, role):
        return self._grid[(principal, role)]

    def listAvailableValues(self):
        # XXX rather use Allow.getName() & co
        return ('Unset', 'Allow', 'Deny')

