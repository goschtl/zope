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

$Id: RolePermissions.py,v 1.1 2002/06/20 15:54:59 jim Exp $
"""

from Zope.ComponentArchitecture import getAdapter
from Zope.App.Security.IRolePermissionManager import IRolePermissionManager
from Zope.App.Security.IRole import IRole
from Zope.App.Security.Settings import Allow

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
        rperms = [permission
                  for permission,setting in rperms
                  if setting==Allow]
        return [{'id': permission.getId(),
                 'title': permission.getTitle(),
                 'checked': ((permission.getId() in rperms) and '1' or None)}
                for permission in self._permissions]        
        
    
