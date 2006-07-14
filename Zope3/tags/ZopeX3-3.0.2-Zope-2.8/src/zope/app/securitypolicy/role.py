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
"""Role implementation

$Id$
"""
from persistent import Persistent
from zope.interface import implements

from zope.app import zapi
from zope.app.container.contained import Contained
from zope.app.securitypolicy.interfaces import IRole
from zope.app.utility import UtilityRegistration


class Role(object):
    implements(IRole)

    def __init__(self, id, title, description=""):
        self.id = id
        self.title = title
        self.description = description


class PersistentRole(Contained, Persistent):
    implements(IRole)

    def __init__(self, title, description=""):
        self.id = '<role not activated>'
        self.title = title
        self.description = description


class RoleRegistration(UtilityRegistration):
    """Role Registration

    We have a custom registration here, since we want active registrations to
    set the id of the role.
    """
    def activated(self):
        role = self.getComponent()
        role.id = self.name

    def deactivated(self):
        role = self.getComponent()
        role.id = '<role not activated>'
    

def checkRole(context, role_id):
    names = [name for name, util in zapi.getUtilitiesFor(IRole, context)]
    if not role_id in names:
        raise ValueError("Undefined role id", role_id)
