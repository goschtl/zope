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

$Id: metaConfigure.py,v 1.1 2002/06/20 15:55:02 jim Exp $
"""
from PermissionRegistry import permissionRegistry as perm_reg
from RoleRegistry import roleRegistry as role_reg
from Zope.Security.SecurityManager import setSecurityPolicy
from PrincipalRegistry import principalRegistry
from Zope.Configuration.Action import Action

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

def unauthenticatedPrincipal(_context, id, title, description=''):
    return [
        Action(
            discriminator = 'unauthenticatedPrincipal',
            callable = principalRegistry.defineDefaultPrincipal,
            args = (id, title, description),
            )
        ]


