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
"""Register security related configuration directives.

$Id$
"""
from zope.app.component.metaconfigure import utility

from zope.security.checker import moduleChecker, Checker, defineChecker
from zope.security.checker import CheckerPublic
from zope.security.management import setSecurityPolicy
from zope.app.security.interfaces import IPermission
from zope.app.security.permission import Permission
from zope.app.security.principalregistry import principalRegistry


def securityPolicy(_context, component):

    _context.action(
            discriminator = 'defaultPolicy',
            callable = setSecurityPolicy,
            args = (component,) )



def protectModule(module, name, permission):
    """Set up a module checker to require a permission to access a name

    If there isn't a checker for the module, create one.
    """

    checker = moduleChecker(module)
    if checker is None:
        checker = Checker({}, {})
        defineChecker(module, checker)

    if permission == 'zope.Public':
        # Translate public permission to CheckerPublic
        permission = CheckerPublic

    # We know a dictionary get method was used because we set it
    protections = checker.get_permissions
    protections[name] = permission


def _names(attributes, interfaces):
    seen = {}
    for name in attributes:
        if not name in seen:
            seen[name] = 1
            yield name
    for interface in interfaces:
        for name in interface:
            if not name in seen:
                seen[name] = 1
                yield name


def allow(context, attributes=(), interface=()):

    for name in _names(attributes, interface):
        context.action(
            discriminator=('http://namespaces.zope.org/zope:module',
                           context.module, name),
            callable = protectModule,
            args = (context.module, name, 'zope.Public'),
            )


def require(context, permission, attributes=(), interface=()):
    for name in _names(attributes, interface):
        context.action(
            discriminator=('http://namespaces.zope.org/zope:module',
                           context.module, name),
            callable = protectModule,
            args = (context.module, name, permission),
            )


def definePermission(_context, id, title, description=''):
    permission = Permission(id, title, description)
    utility(_context, IPermission, permission, name=id)


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

def redefinePermission(_context, from_, to):
    _context = _context.context
    
    # check if context has any permission mappings yet
    if not hasattr(_context, 'permission_mapping'):
        _context.permission_mapping={}

    _context.permission_mapping[from_] = to
