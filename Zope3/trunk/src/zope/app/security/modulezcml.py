##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""ZCML directive for module security declarations


$Id: modulezcml.py,v 1.1 2003/09/02 20:47:05 jim Exp $
"""
from __future__ import generators

import zope.interface
import zope.schema
import zope.configuration.fields
import zope.configuration.config
from zope.app.security.protectclass import checkPermission
from zope.security.checker import moduleChecker, Checker, defineChecker
from zope.security.checker import CheckerPublic

class IModule(zope.interface.Interface):

    module = zope.configuration.fields.GlobalObject(
        __doc__ = "Module",
        )

class IAllow(zope.interface.Interface):

    attributes = zope.configuration.fields.Tokens(
        __doc__ = """Attributes

        The attributes to provide access to.
        """,
        value_type = zope.configuration.fields.PythonIdentifier(),
        required=False,
        )

    interface = zope.configuration.fields.Tokens(
        __doc__ = """Interface

        Interfaces whos names to provide access to.  Access will be
        provided to all of the names defined by the
        interface(s). Multiple interfaces can be supplied.
        
        """,
        value_type = zope.configuration.fields.GlobalObject(
           value_type=zope.schema.InterfaceField()
           ),
        required=False,
        )

class IRequire(zope.interface.Interface):

    permission = zope.schema.Id(
        __doc__ = """Permission ID

        The id of the permission to require.
        """,
        )


def protectModule(module, name, permission):
    """Set up a module checker to require a permission to access a name

    If there isn't a checker for the module, create one.
    """

    checkPermission(permission)

    checker = moduleChecker(module)
    if checker is None:
        checker = Checker({}, {})
        defineChecker(module, checker)

    if permission == 'zope.Public':
        # Translate public permission to CheckerPublic
        permission = CheckerPublic

    # We know a dictionary get method was used because we set it
    protections = checker.getPermission_func().__self__
    protections[name] = permission

def _names(attributes, interface):
    seen = {}
    for name in attributes:
        if not name in seen:
            seen[name] = 1
            yield name
    for interface in interface:
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
