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

Revision information:
$Id: role.py,v 1.2 2002/12/25 14:13:19 jim Exp $
"""

from zope.app.security.registries.roleregistry import Role
from persistence import Persistent

class Role(Role, Persistent):
    "Persistent Role"




"""

Revision information:
$Id: role.py,v 1.2 2002/12/25 14:13:19 jim Exp $
"""
from zope.app.container.btree import BTreeContainer
from zope.app.interfaces.security import IRoleService
from zope.app.interfaces.container import IContainer
from zope.proxy.context import ContextMethod
from zope.app.component.nextservice import getNextService

class ILocalRoleService(IRoleService, IContainer):
    """TTW manageable role service"""

class RoleService(BTreeContainer):

    __implements__ = ILocalRoleService

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
    getRole = ContextMethod(getRole)

    def getRoles(wrapped_self):
        '''See interface IRoleService'''
        roles = list(wrapped_self.values())
        roleserv = getNextService(wrapped_self, 'Roles')
        if roleserv:
            roles.extend(roleserv.getRoles())
        return roles
    getRoles = ContextMethod(getRoles)

    #
    ############################################################
