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

$Id: roleservice.py,v 1.1 2004/02/27 12:46:32 philikon Exp $
"""

from zope.interface import implements
from zope.app.interfaces.services.service import ISimpleService
from zope.app.securitypolicy.interfaces import IRoleService
from zope.app.securitypolicy.interfaces import IRole

class Role:
    implements(IRole)

    def __init__(self, id, title): self._id, self._title = id, title
    def getId(self): return self._id
    def getTitle(self): return self._title
    def getDescription(self): return ''

class RoleService:
    implements(IRoleService, ISimpleService)

    def __init__(self, **kw):
        self._roles = r = {}
        for id, title in kw.items(): r[id]=Role(id, title)

    def getRole(self, rid):
        return self._roles.get(rid)

    def getRoles(self):
        return self._roles.values()
