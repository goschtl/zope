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
"""PermissionService implementation for testing

$Id: PermissionService.py,v 1.2 2002/06/10 23:28:16 jim Exp $
"""

from Zope.App.Security.IPermissionService import IPermissionService
from Zope.App.Security.IPermission import IPermission

class Permission:

    __implements__ = IPermission

    def __init__(self, id, title): self._id, self._title = id, title
    def getId(self): return self._id
    def getTitle(self): return self._title
    def getDescription(self): return ''

class PermissionService:

    __implements__ = IPermissionService

    def __init__(self, **kw):
        self._permissions = r = {}
        for id, title in kw.items(): r[id]=Permission(id, title) 

    # Implementation methods for interface
    # Zope.App.Security.IPermissionService.

    def getPermission(self, rid):
        '''See interface IPermissionService'''
        return self._permissions.get(rid)

    def getPermissions(self):
        '''See interface IPermissionService'''
        return self._permissions.values()
