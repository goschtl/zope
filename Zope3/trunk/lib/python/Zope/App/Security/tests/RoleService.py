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
"""RoleService implementation for testing

$Id: RoleService.py,v 1.2 2002/06/10 23:28:16 jim Exp $
"""

from Zope.App.Security.IRoleService import IRoleService
from Zope.App.Security.IRole import IRole

class Role:

    __implements__ = IRole

    def __init__(self, id, title): self._id, self._title = id, title
    def getId(self): return self._id
    def getTitle(self): return self._title
    def getDescription(self): return ''

class RoleService:

    __implements__ = IRoleService    

    def __init__(self, **kw):
        self._roles = r = {}
        for id, title in kw.items(): r[id]=Role(id, title) 

    # Implementation methods for interface
    # Zope.App.Security.IRoleService.

    def getRole(self, rid):
        '''See interface IRoleService'''
        return self._roles.get(rid)

    def getRoles(self):
        '''See interface IRoleService'''
        return self._roles.values()
