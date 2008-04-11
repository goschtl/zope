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
""" z3ext:preferenceGroup directive implementation

$Id$
"""
from zope import interface
from zope.schema import Int
from zope.component import getUtility, queryUtility, getGlobalSiteManager
from zope.schema.interfaces import IField

from zope.security.zcml import Permission
from zope.security.checker import Checker, CheckerPublic

from zope.interface.common.mapping import IEnumerableMapping

from zope.component.zcml import utility
from zope.component.interface import provideInterface

from zope.configuration import fields
from zope.configuration.exceptions import ConfigurationError

from zope.app.security.protectclass import \
    protectName, protectSetAttribute, protectLikeUnto

from interfaces import IPreferenceGroup
from preference import PreferenceGroup
from preferencetype import PreferenceType
from utils import PrincipalChecker


class IPreferenceGroupDirective(interface.Interface):
    """Register a preference group."""

    id = fields.PythonIdentifier(
        title=u"Id",
        description=u"""
            Id of the preference group used to access the group. The id should
            be a valid path in the preferences tree.""",
        required=True)

    for_ = fields.GlobalInterface(
        title=u"For",
        description=u"Principal interface to use this preference for.",
        required=False)

    schema = fields.GlobalInterface(
        title=u"Schema",
        description=u"Schema of the preference group used defining the "
                    u"preferences of the group.",
        required=False)

    title = fields.MessageID(
        title=u"Title",
        description=u"Title of the preference group used in UIs.",
        required=True)

    description = fields.MessageID(
        title=u"Description",
        description=u"Description of the preference group used in UIs.",
        required=False)

    class_ = fields.GlobalObject(
        title=u"Class",
        description=u"Custom IPreferenceGroup implementation.",
        required=False)

    provides = fields.Tokens(
	title = u'Provides',
        required = False,
        value_type = fields.GlobalInterface())

    permission = Permission(
        title = u'Permission',
        description = u'Default access permission.',
        required = False)

    tests = fields.Tokens(
	title = u"Tests",
        description = u'Tests for check availability.',
        value_type = fields.GlobalObject(),
	required = False)

    order = Int(
        title = u'Order',
        default = 999999,
        required = False)


class PreferenceGroupDirective(object):

    def __init__(self, _context, id, title,
                 for_=None, schema=interface.Interface,
                 description=u'', category=False,
                 class_=None, provides=[], permission=CheckerPublic,
                 tests=(), order = 9999):

        Class = PreferenceType(str(id), schema, class_, title, description)
        Class.order = order

        if interface.interfaces.IInterface.providedBy(for_):
            tests = tests + (PrincipalChecker(for_),)

        group = Class(tests)

        utility(_context, IPreferenceGroup, group, name=id)

        interface.classImplements(Class, *provides)

        self._class = Class
        self._context = _context
        self._permission = permission

        self.require(_context, permission, interface=(IPreferenceGroup, schema))
        self.require(_context, 'z3ext.ModifyPreference', set_schema=(schema,))
        self.require(_context, CheckerPublic,
                     interface=(IEnumerableMapping,), attributes=('isAvailable',))

        _context.action(
            discriminator=('z3ext:preferences', group),
            callable=addSubgroup, args=(group,))

    def require(self, _context,
                permission=None, attributes=None, interface=None,
                like_class=None, set_attributes=None, set_schema=None):
        """Require a permission to access a specific aspect"""
        if like_class:
            self.__mimic(_context, like_class)

        if not (interface or attributes or set_attributes or set_schema):
            if like_class:
                return
            raise ConfigurationError("Nothing required")

        if not permission:
            raise ConfigurationError("No permission specified")

        if interface:
            for i in interface:
                if i:
                    self.__protectByInterface(i, permission)

        if attributes:
            self.__protectNames(attributes, permission)

        if set_attributes:
            self.__protectSetAttributes(set_attributes, permission)

        if set_schema:
            for s in set_schema:
                self.__protectSetSchema(s, permission)

    def __mimic(self, _context, class_):
        """Base security requirements on those of the given class"""
        _context.action(
            discriminator=('z3ext:preferences:mimic', self._class),
            callable=protectLikeUnto,
            args=(self._class, class_),
            )

    def allow(self, _context, attributes=None, interface=None):
        """Like require, but with permission_id zope.Public"""
        return self.require(_context, self._permission, attributes, interface)

    def __protectByInterface(self, interface, permission_id):
        "Set a permission on names in an interface."
        for n, d in interface.namesAndDescriptions(1):
            self.__protectName(n, permission_id)

        self._context.action(
            discriminator = None,
            callable = provideInterface,
            args = (interface.__module__+'.'+interface.getName(), interface))

    def __protectName(self, name, permission_id):
        "Set a permission on a particular name."
        self._context.action(
            discriminator = ('z3ext:preferences:protectName', object()),
            callable = protectName,
            args = (self._class, name, permission_id))

    def __protectNames(self, names, permission_id):
        "Set a permission on a bunch of names."
        for name in names:
            self.__protectName(name, permission_id)

    def __protectSetAttributes(self, names, permission_id):
        "Set a permission on a bunch of names."
        for name in names:
            self._context.action(
                discriminator = (
                    'z3ext:preferences:protectSetAttribute', object()),
                callable = protectSetAttribute,
                args = (self._class, name, permission_id))

    def __protectSetSchema(self, schema, permission_id):
        "Set a permission on a bunch of names."
        _context = self._context

        for name in schema:
            field = schema[name]
            if IField.providedBy(field) and not field.readonly:
                _context.action(
                    discriminator = (
                        'z3ext:preferences:protectSetAttribute', object()),
                    callable = protectSetAttribute,
                    args = (self._class, name, permission_id))

        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = (schema.__module__+'.'+schema.getName(), schema))


def addSubgroup(group):
    if '.' in group.__id__:
        parentId = group.__id__.split('.')[0]
    else:
        parentId = ''

    parent = queryUtility(IPreferenceGroup, parentId)
    if parent is None:
        parent = getGlobalSiteManager().getUtility(IPreferenceGroup, parentId)

    parent.add(group.__name__)
    group.__parent__ = parent
