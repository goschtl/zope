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

$Id: metaConfigure.py,v 1.2 2002/06/10 23:28:16 jim Exp $
"""
from PermissionRegistry import permissionRegistry as perm_reg
from RoleRegistry import roleRegistry as role_reg
from Zope.Security.SecurityManager import setSecurityPolicy
from PrincipalRegistry import principalRegistry
from RolePermissionManager import rolePermissionManager as role_perm_mgr
from PrincipalPermissionManager import principalPermissionManager \
        as principal_perm_mgr
from PrincipalRoleManager import principalRoleManager as principal_role_mgr
from Zope.Configuration.Action import Action

def defaultPolicy(_context, name):
    policy = _context.resolve(name)
    if callable(policy):
        policy = policy()
    return [
        Action(
            discriminator = 'defaultPolicy',
            callable = setSecurityPolicy,
            args = (policy,),
            )
        ]

def definePermission(_context, id, title, description=''):
    return [
        Action(
            discriminator = ('definePermission', id),
            callable = perm_reg.definePermission,
            args = (id, title, description),
            )
        ]

def defineRole(_context, id, title, description=''):
    return [
        Action(
            discriminator = ('defineRole', id),
            callable = role_reg.defineRole,
            args = (id, title, description),
            )
        ]

def principal(_context, id, title, login, password, description=''):
    return [
        Action(
            discriminator = ('principal', id),
            callable = principalRegistry.definePrincipal,
            args = (id, title, description, login, password),
            )
        ]

def defaultPrincipal(_context, id, title, description=''):
    return [
        Action(
            discriminator = 'defaultPrincipal',
            callable = principalRegistry.defineDefaultPrincipal,
            args = (id, title, description),
            )
        ]

def grantPermissionToRole(_context, permission, role):
    return [
        Action(
            discriminator = ('grantPermissionToRole', permission, role),
            callable = role_perm_mgr.grantPermissionToRole,
            args = (permission, role),
            )
        ]

def grantPermissionToPrincipal(_context, permission, principal):
    return [
        Action(
            discriminator = ('grantPermissionToPrincipal', 
                             permission,
                             principal),
            callable = principal_perm_mgr.grantPermissionToPrincipal,
            args = (permission, principal),
        )
    ]

def assignRoleToPrincipal(_context, role, principal):
    return [
        Action(
            discriminator = ('assignRoleToPrincipal', role, principal),
            callable = principal_role_mgr.assignRoleToPrincipal,
            args = (role, principal),
        )
    ]


