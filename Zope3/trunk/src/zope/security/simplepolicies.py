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
""" Simple ISecurityPolicy implementations."""

from zope.security.interfaces import ISecurityPolicy
from zope.security.management import system_user
import zope.security.checker

class ParanoidSecurityPolicy:
    """
        Deny all access.
    """
    __implements__ = ISecurityPolicy

    def checkPermission(self, permission, object, context):
        if permission is zope.security.checker.CheckerPublic:
            return 1
        if (context.user is system_user   # no user
            and not context.stack  # no untrusted code
            ):
            return 1 # Nobody not to trust!

        return 0

class PermissiveSecurityPolicy:
    """
        Allow all access
    """
    __implements__ = ISecurityPolicy

    def checkPermission(self, permission, object, context):
        return 1
