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
""" Register security related configuration directives.

$Id: metaconfigure.py,v 1.2 2002/12/25 14:13:16 jim Exp $
"""
from zope.app.security.grants.rolepermissionmanager \
     import rolePermissionManager as role_perm_mgr
from zope.app.security.grants.principalpermissionmanager \
     import principalPermissionManager as principal_perm_mgr
from zope.app.security.grants.principalrolemanager \
     import principalRoleManager as principal_role_mgr
from zope.configuration.action import Action
from zope.configuration.exceptions import ConfigurationError


def grant(_context, principal=None, role=None, permission=None):
    if (  (principal is not None)
        + (role is not None)
        + (permission is not None)
          ) != 2:
        raise ConfigurationError(
            "Exactly two of the principal, role, and permission attributes "
            "must be specified")

    if principal:
        if role:
            return [
                Action(
                discriminator = ('grantRoleToPrincipal', role, principal),
                callable = principal_role_mgr.assignRoleToPrincipal,
                args = (role, principal),
                )
                ]
        if permission:
            return [
                Action(
                discriminator = ('grantPermissionToPrincipal',
                                 permission,
                                 principal),
                callable = principal_perm_mgr.grantPermissionToPrincipal,
                args = (permission, principal),
                )
                ]
    else:
        return [
            Action(
            discriminator = ('grantPermissionToRole', permission, role),
            callable = role_perm_mgr.grantPermissionToRole,
            args = (permission, role),
            )
            ]
