##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.component
from zope.app.security.interfaces import IAuthentication

from z3c.authenticator import interfaces


class PrincipalBase(object):
    """Base class for IAuthenticatedPrincipal and IFoundPrincipal principals.
    """

    title = None

    def __init__(self, principal):
        """We offer no access to the principal object itself."""
        self.id = principal.__name__
        self.title = principal.title
        self.description = principal.description
        self.groups = []

    @property
    def allGroups(self):
        if self.groups:
            seen = set()
            auth = zope.component.getUtility(IAuthentication)
            stack = [iter(self.groups)]
            while stack:
                try:
                    group_id = stack[-1].next()
                except StopIteration:
                    stack.pop()
                else:
                    if group_id not in seen:
                        yield group_id
                        seen.add(group_id)
                        group = auth.getPrincipal(group_id)
                        stack.append(iter(group.groups))

    def __repr__(self):
        return "<%s %s>" %(self.__class__.__name__, self.id)


class AuthenticatedPrincipal(PrincipalBase):
    """Default IAuthenticatedPrincipal principal."""

    zope.component.adapts(interfaces.IUser)

    zope.interface.implements(interfaces.IAuthenticatedPrincipal)


class FoundPrincipal(PrincipalBase):
    """Default IFoundPrincipal principal."""

    zope.component.adapts(interfaces.IUser)

    zope.interface.implements(interfaces.IFoundPrincipal)
