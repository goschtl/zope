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
"""Permission to Roles Map implementation

$Id$
"""
from zope.interface import implements

from zope.app.security.interfaces import IPermission
from zope.app.security.settings import Unset
from zope.app.securitypolicy.interfaces import IRolePermissionManager

class PermissionRoles(object):

    implements(IPermission)

    def __init__(self, permission, context, roles):
        self._permission = permission
        self._context    = context
        self._roles      = roles

    def _getId(self):
        return self._permission.id

    id = property(_getId)

    def _getTitle(self):
        return self._permission.title

    title = property(_getTitle)

    def _getDescription(self):
        return self._permission.description

    description = property(_getDescription)

    def roleSettings(self):
        """
        Returns the list of setting names of each role for this permission.
        """
        prm = IRolePermissionManager(self._context)
        proles = prm.getRolesForPermission(self._permission.id)
        settings = {}
        for role, setting in proles:
            settings[role] = setting.getName()
        nosetting = Unset.getName()
        return [settings.get(role.id, nosetting) for role in self._roles]
