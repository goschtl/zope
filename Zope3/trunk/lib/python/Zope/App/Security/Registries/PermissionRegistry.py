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
""" Global permission registry."""

PREFIX = 'Global Permission'
SUFFIX = 'Zope.Public'
DESCRIP = 'Anybody can do this'

from Zope.App.Security.Registries.RegisteredObject import RegisteredObject
from Zope.App.Security.Registries.Registry import Registry
from Zope.App.Security.IPermission import IPermission
from Zope.App.Security.IPermissionService import IPermissionService


class Permission(RegisteredObject):
    __implements__ = IPermission


class PermissionRegistry(Registry):
    __implements__ = IPermissionService
    
    def __init__(self, prefix=PREFIX):
        Registry.__init__(self, Permission)
        self._prefix = prefix

    def definePermission(self, permission, title, description=''):
        """Define a new permission object, register, and return it.

        permission is the permission name, must be globally unique

        title is the permission title, human readable.

        description (optional) is human readable
        """
        if permission.startswith('.'):
            raise ValueError("permissions must not start with a '.'")
        return self.register(permission, title, description)

    def definedPermission(self, permission_id):
        """Return true if named permission is registered, otherwise return
        false
        """
        return self.is_registered(permission_id)

    def getPermission(self, permission_id):
        """Return permission object registered as permission_id.

        If no named permission is registered KeyError is raised.

        """
        return self.getRegisteredObject(permission_id)

    def getPermissions(self):
        """Return all registered permission objects.
        """
        return self.getRegisteredObjects()

    def _clear(self):
        Registry._clear(self)
        self.definePermission(
            'Zope.Public', 'Public',
            """Special permission used for resources that are always public

            The public permission is effectively an optimization, sine
            it allows security computation to be bypassed.
            """
            )

permissionRegistry = PermissionRegistry()

# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from Zope.Testing.CleanUp import addCleanUp
addCleanUp(permissionRegistry._clear)
del addCleanUp
