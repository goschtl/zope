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

$Id: rolepermissions.py,v 1.2 2002/12/25 14:13:16 jim Exp $
"""

from zope.component import getAdapter
from zope.app.interfaces.security import IRolePermissionManager
from zope.app.interfaces.security import IRole
from zope.app.security.settings import Unset

class RolePermissions:

    __implements__ = IRole

    def __init__(self, role, context, permissions):
        self._role = role
        self._context = context
        self._permissions = permissions

    def getId(self):
        return self._role.getId()

    def getTitle(self):
        return self._role.getTitle()

    def getDescription(self):
        return self._role.getDescription()

    def permissionsInfo(self):
        prm = getAdapter(self._context, IRolePermissionManager)
        rperms = prm.getPermissionsForRole(self._role.getId())
        settings = {}
        for permission, setting in rperms:
            settings[permission] = setting.getName()
        nosetting = Unset.getName()
        return [{'id': permission.getId(),
                 'title': permission.getTitle(),
                 'setting': settings.get(permission.getId(), nosetting)}
                for permission in self._permissions]
