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
"""Simple 'ISecurityPolicy' implementations.

$Id: simplepolicies.py,v 1.6 2004/02/20 20:42:12 srichter Exp $
"""

from zope.security.interfaces import ISecurityPolicy
from zope.security.management import system_user
import zope.security.checker
from zope.interface import implements

class ParanoidSecurityPolicy:
    """Deny all access."""
    implements(ISecurityPolicy)

    def checkPermission(self, permission, object, context):
        if permission is zope.security.checker.CheckerPublic:
            return True
        if (context.user is system_user   # no user
            and not context.stack  # no untrusted code
            ):
            return True # Nobody not to trust!

        return False

class PermissiveSecurityPolicy:
    """Allow all access."""
    implements(ISecurityPolicy)

    def checkPermission(self, permission, object, context):
        return True
