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
$Id: role.py,v 1.2 2004/03/03 10:38:51 philikon Exp $
"""

from persistence import Persistent
from zope.interface import implements
from zope.component import getService

from zope.app.container.btree import BTreeContainer
from zope.app.container.interfaces import IContainer
from zope.app.component.nextservice import getNextService
from zope.app.interfaces.services.service import ISimpleService

from zope.app.securitypolicy.roleregistry import Role
from zope.app.securitypolicy.interfaces import IRoleService

class Role(Role, Persistent):
    "Persistent Role"

class ILocalRoleService(IRoleService, IContainer):
    """TTW manageable role service"""

class RoleService(BTreeContainer):

    implements(ILocalRoleService, ISimpleService)

    def getRole(wrapped_self, rid):
        '''See interface IRoleService'''
        try:
            return wrapped_self[rid]
        except KeyError:
            # We failed locally: delegate to a higher-level service.
            sv = getNextService(wrapped_self, 'Roles')
            if sv:
                return sv.getRole(rid)
            raise # will be original Key Error

    def getRoles(wrapped_self):
        '''See interface IRoleService'''
        roles = list(wrapped_self.values())
        roleserv = getNextService(wrapped_self, 'Roles')
        if roleserv:
            roles.extend(roleserv.getRoles())
        return roles

def checkRole(context, role_id):
    if not getService(context, 'Roles').getRole(role_id):
        raise ValueError("Undefined role id", role_id)
