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
"""Global role registry."""

PREFIX = 'Global Role'

from zope.app.security.registries.registeredobject import RegisteredObject
from zope.app.security.registries.registry import Registry
from zope.app.interfaces.security import IRole
from zope.app.interfaces.security import IRoleService
from zope.app.interfaces.services.service import ISimpleService
from zope.interface import implements

class Role(RegisteredObject):
    implements(IRole)


class RoleRegistry(Registry):
    implements(IRoleService, ISimpleService)

    def __init__(self, prefix=PREFIX):
        Registry.__init__(self, Role)
        self._prefix = prefix

    def _make_global_id(self, suffix):
        return self._prefix + '.' + suffix

    def defineRole(self, role, title, description=None):
        """Define a new role object, register, and return it.

        role is the role name.

        title is the role title, human readable.

        description (optional) is human readable
        """
        if description is None:
            description = ''
        id = role
        return self.register(id, title, description)

    def definedRole(self, id):
        """Return true if named role is registered, otherwise return false
        """
        return self.is_registered(id)

    def getRole(self, id):
        """Return role object registered as name.

        If no named role is registered KeyError is raised.
        """
        return self.getRegisteredObject(id)

    def getRoles(self):
        """Return all registered role objects.
        """
        return self.getRegisteredObjects()

    def _clear(self):
        # Standard roles
        Registry._clear(self)
        self.register("Anonymous", "Everybody",
                      "All users have this role implicitly")

roleRegistry = RoleRegistry()


# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from zope.testing.cleanup import addCleanUp
addCleanUp(roleRegistry._clear)
del addCleanUp
