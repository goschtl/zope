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

$Id: metaconfigure.py,v 1.1 2004/02/27 12:46:31 philikon Exp $
"""
from zope.configuration.exceptions import ConfigurationError

from zope.app.securitypolicy.roleregistry import roleRegistry as role_reg
from zope.app.securitypolicy.rolepermission \
     import rolePermissionManager as role_perm_mgr
from zope.app.securitypolicy.principalpermission \
     import principalPermissionManager as principal_perm_mgr
from zope.app.securitypolicy.principalrole \
     import principalRoleManager as principal_role_mgr


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
            _context.action(
                discriminator = ('grantRoleToPrincipal', role, principal),
                callable = principal_role_mgr.assignRoleToPrincipal,
                args = (role, principal) )

        if permission:
            _context.action(
                discriminator = ('grantPermissionToPrincipal',
                                 permission,
                                 principal),
                callable = principal_perm_mgr.grantPermissionToPrincipal,
                args = (permission, principal) )
    else:
        _context.action(
            discriminator = ('grantPermissionToRole', permission, role),
            callable = role_perm_mgr.grantPermissionToRole,
            args = (permission, role) )

def defineRole(_context, id, title, description=''):
    _context.action(
            discriminator = ('defineRole', id),
            callable = role_reg.defineRole,
            args = (id, title, description) )

