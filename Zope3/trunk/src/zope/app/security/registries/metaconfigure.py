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

$Id: metaconfigure.py,v 1.5 2003/08/02 20:05:39 srichter Exp $
"""
from zope.app.security.registries.permissionregistry import \
     permissionRegistry as perm_reg
from zope.app.security.registries.roleregistry import roleRegistry as role_reg
from zope.app.security.registries.principalregistry import principalRegistry

def definePermission(_context, id, title, description=''):
    _context.action(
        discriminator = ('definePermission', id),
        callable = perm_reg.definePermission,
        args = (id, title, description) )

def defineRole(_context, id, title, description=''):
    _context.action(
            discriminator = ('defineRole', id),
            callable = role_reg.defineRole,
            args = (id, title, description) )

def principal(_context, id, title, login, password, description=''):
    _context.action(
        discriminator = ('principal', id),
        callable = principalRegistry.definePrincipal,
        args = (id, title, description, login, password) )

def unauthenticatedPrincipal(_context, id, title, description=''):
    _context.action(
        discriminator = 'unauthenticatedPrincipal',
        callable = principalRegistry.defineDefaultPrincipal,
        args = (id, title, description) )
