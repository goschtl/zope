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
"""Simple 'ISecurityPolicy' implementations.

$Id$
"""

from zope.interface import implements
from zope.security.interfaces import ISecurityPolicy
from zope.security.management import system_user
from zope.security.simpleinteraction import createInteraction \
                                            as _createInteraction
import zope.security.checker

class ParanoidSecurityPolicy:
    """Deny all access."""
    implements(ISecurityPolicy)

    createInteraction = staticmethod(_createInteraction)

    def checkPermission(self, permission, object, interaction):
        if permission is zope.security.checker.CheckerPublic:
            return True

        if interaction is None:
            return False

        users = [p.principal for p in interaction.participations]
        if len(users) == 1 and users[0] is system_user:
            return True # Nobody not to trust!

        return False


class PermissiveSecurityPolicy:
    """Allow all access."""
    implements(ISecurityPolicy)

    createInteraction = staticmethod(_createInteraction)

    def checkPermission(self, permission, object, interaction):
        return True

