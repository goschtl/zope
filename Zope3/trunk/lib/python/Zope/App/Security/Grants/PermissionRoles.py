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

$Id: PermissionRoles.py,v 1.2 2002/06/24 16:00:44 efge Exp $
"""

from Zope.ComponentArchitecture import getAdapter
from Zope.App.Security.IRolePermissionManager import IRolePermissionManager
from Zope.App.Security.IPermission import IPermission
from Zope.App.Security.Settings import Unset, Allow, Deny

class PermissionRoles:

    __implements__ = IPermission

    def __init__(self, permission, context, roles):
        self._permission = permission
        self._context    = context
        self._roles      = roles

    def getId(self):
        return self._permission.getId()

    def getTitle(self):
        return self._permission.getTitle()

    def getDescription(self):
        return self._permission.getDescription()

    def roleSettings(self):
        """
        Returns the list of setting names of each role for this permission.
        """
        prm = getAdapter(self._context, IRolePermissionManager)
        proles = prm.getRolesForPermission(self._permission.getId())
        settings = {}
        for role, setting in proles:
            settings[role] = setting.getName()
        nosetting = Unset.getName()
        return [settings.get(role.getId(), nosetting) for role in self._roles]

    def rolesInfo(self):
        prm = getAdapter(self._context, IRolePermissionManager)
        proles = prm.getRolesForPermission(self._permission.getId())
        proles = [role for role,setting in proles if setting==Allow]
        return [{'id': role.getId(),
                 'title': role.getTitle(),
                 'checked': ((role.getId() in proles) and '1' or None)}
                for role in self._roles]
