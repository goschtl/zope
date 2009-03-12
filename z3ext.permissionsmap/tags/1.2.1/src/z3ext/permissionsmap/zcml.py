##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
""" zcml directive

$Id$
"""
from zope.component import globalregistry
from zope.component import getUtility, queryUtility, getUtilitiesFor

from zope import schema, interface, component
from zope.security.zcml import Permission
from zope.configuration.fields import Tokens, GlobalObject
from zope.securitypolicy.interfaces import IRole

from interfaces import IPermissionsMap
from interfaces import IDefaultPermissionsMap
from permissionsmap import PermissionsMap


class IPermissionsMapDirective(interface.Interface):
    """ define permissions map directive"""

    name = schema.TextLine(
	title=u"Name",
	description=u"Permissions map identifier.",
	required=True)

    for_ = GlobalObject(
	title=u"For",
	required=False)

    title = schema.TextLine(
	title=u"Title",
	description=u"Permissions map title.",
	required=False)

    description = schema.TextLine(
	title=u"Description",
	description=u"Permissions map description.",
	required=False)

    override = schema.Bool(
	title=u"Override",
	description=u"Allow override sub directives for this declaration.",
	required=False,
        default=True)


class IGrantDirective(interface.Interface):

    role = Tokens(
        title=u"Role",
        description=u"Specifies the role.",
        required=True,
	value_type=schema.TextLine())

    permission = Tokens(
        title=u"Permission",
        description=u"Specifies the permission to be mapped.",
        required=True,
	value_type=Permission())


class IDenyDirective(interface.Interface):

    role = Tokens(
        title=u"Role",
        description=u"Specifies the role.",
        required=True,
	value_type=schema.TextLine())

    permission = Tokens(
        title=u"Permission",
        description=u"Specifies the permission to be mapped.",
        required=True,
        value_type=Permission())


class IUnsetDirective(interface.Interface):

    role = Tokens(
        title=u"Role",
        description=u"Specifies the role.",
        required=True,
	value_type=schema.TextLine())

    permission = Tokens(
        title=u"Permission",
        description=u"Specifies the permission to be mapped.",
        required=True,
        value_type=Permission())


class IGrantAllDirective(interface.Interface):

    permission = Tokens(
        title=u"Permission",
        description=u"Specifies the permission to be mapped.",
        required=True,
        value_type=Permission())


class IDenyAllDirective(interface.Interface):

    permission = Tokens(
        title=u"Permission",
        description=u"Specifies the permission to be mapped.",
        required=True,
        value_type=Permission())


class IUnsetAllDirective(interface.Interface):

    permission = Tokens(
        title=u"Permission",
        description=u"Specifies the permission to be mapped.",
        required=True,
        value_type=Permission())


class ClassPermissionsFactory(object):

    def __init__(self, permissionsmap):
        self.permissionsmap = permissionsmap

    def __call__(self, context):
        return self.permissionsmap


def permissionsHandler(name, for_, title, description):
    # check if map already exists
    sm = globalregistry.globalSiteManager

    perms = sm.queryUtility(IPermissionsMap, name)
    if perms is not None:
        return

    # register map as utility
    perms = PermissionsMap(name, title, description)
    sm.registerUtility(perms, IPermissionsMap, name)

    if for_ is not None:
        # register map as adapter for for_
        interface.alsoProvides(perms, IDefaultPermissionsMap)
        factory = ClassPermissionsFactory(perms)
        sm.registerAdapter(factory, (for_,), IPermissionsMap, name)


def directiveHandler(name, method, permissions, roles, check=False):
    sm = globalregistry.globalSiteManager

    permissionmap = sm.getUtility(IPermissionsMap, name)

    for role in roles:
        for permission in permissions:
            if not check:
                getattr(permissionmap, method)(permission, role, False)
            else:
                getattr(permissionmap, method)(permission, role)


def directiveHandlerAll(name, method, permissions, attr):
    sm = globalregistry.globalSiteManager

    permissionmap = sm.getUtility(IPermissionsMap, name)

    if attr == 'unsetall':
        for role_id, role in getUtilitiesFor(IRole):
            for permission in permissions:
                getattr(permissionmap, method)(permission, role_id)
    else:
        lst = getattr(permissionmap, attr)
        for permission in permissions:
            if permission not in lst:
                lst.append(permission)


class permissionsMapDirective(object):

    def __init__(self, _context, name, for_=None, 
                 title='', description='', override=True):
        self.name = name
        self.override = override

        _context.action(
            discriminator = ('z3ext.permissions', name, hash(self)),
            callable = permissionsHandler,
            args = (name, for_, title, description))

    def discriminator(self, data):
        if self.override:
            data = data + (object(),)
        return data

    def grant(self, _context, role, permission):
        _context.action(
            discriminator = self.discriminator(
                ('z3ext.permissions.grant', 
                 self.name, tuple(role), tuple(permission))),
            callable = directiveHandler,
            args = (self.name, 'grantPermissionToRole', permission, role))

    def deny(self, _context, role, permission):
        _context.action(
            discriminator = self.discriminator(
                ('z3ext.permissions.deny', 
                 self.name, tuple(role), tuple(permission))),
            callable = directiveHandler,
            args = (self.name, 'denyPermissionToRole', permission, role))

    def unset(self, _context, role, permission):
        _context.action(
            discriminator = self.discriminator(
                ('z3ext.permissions.unset', 
                 self.name, tuple(role), tuple(permission))),
            callable = directiveHandler,
            args = (self.name, 'unsetPermissionFromRole',
                    permission, role, True))

    def grantAll(self, _context, permission):
        _context.action(
            discriminator = self.discriminator(
                ('z3ext.permissions.grantAll', 
                 self.name, tuple(permission))),
            callable = directiveHandlerAll,
            args = (self.name, 'grantPermissionToRole', permission, 'grantall'))

    def denyAll(self, _context, permission):
        _context.action(
            discriminator = self.discriminator(
                ('z3ext.permissions.denyAll', 
                 self.name, tuple(permission))),
            callable = directiveHandlerAll,
            args = (self.name, 'denyPermissionToRole', permission, 'denyall'))

    def unsetAll(self, _context, permission):
        _context.action(
            discriminator = self.discriminator(
                ('z3ext.permissions.unsetAll', 
                 self.name, tuple(permission))),
            callable = directiveHandlerAll,
            args = (self.name, 'unsetPermissionFromRole', permission, 'unsetall'))
