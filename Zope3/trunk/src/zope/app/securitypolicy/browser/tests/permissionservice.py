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

$Id: permissionservice.py,v 1.1 2004/02/27 12:46:32 philikon Exp $
"""

from zope.app.interfaces.security import IPermissionService
from zope.app.interfaces.security import IPermission
from zope.app.interfaces.services.service import ISimpleService
from zope.interface import implements

class Permission:

    implements(IPermission)

    def __init__(self, id, title): self._id, self._title = id, title
    def getId(self): return self._id
    def getTitle(self): return self._title
    def getDescription(self): return ''

class PermissionService:

    implements(IPermissionService, ISimpleService)

    def __init__(self, **kw):
        self._permissions = r = {}
        for id, title in kw.items(): r[id]=Permission(id, title)

    def getPermission(self, rid):
        '''See interface IPermissionService'''
        return self._permissions.get(rid)

    def getPermissions(self):
        '''See interface IPermissionService'''
        return self._permissions.values()
