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
"""Content Component Definition and Instance

$Id: content.py,v 1.3 2003/08/17 06:08:33 philikon Exp $
"""
__metaclass__ = type

from persistence import Persistent
from persistence.dict import PersistentDict
from zope.app import zapi
from zope.app.interfaces.container import IAdding
from zope.app.interfaces.utilities.content import \
     IContentComponentDefinition, IContentComponentInstance
from zope.app.services.menu import LocalBrowserMenuItem
from zope.app.services.servicenames import BrowserMenu
from zope.app.services.utility import UtilityRegistration
from zope.context import ContextMethod
from zope.interface import directlyProvides, implements
from zope.schema import getFields
from zope.security.checker import CheckerPublic, Checker, defineChecker


class ContentComponentDefinition(Persistent):

    implements(IContentComponentDefinition)

    def __init__(self, name=u'', schema=None):
        self.name = name
        self.schema = schema
        self.permissions = PersistentDict()


class ContentComponentDefinitionRegistration(UtilityRegistration):
    """Content Component Registration"""

    menuitem_id = None
    menu = None

    def activated(self):
        """Once activated, we have to register the new Content Object with the
        appropriate menu.
        """
        service = zapi.getService(self, BrowserMenu)
        # XXX: Should use queryInheritedMenu()
        self.menu = service.queryLocalMenu('add_content')
        # Creating the menu item
        # XXX: Should be configurable
        item = LocalBrowserMenuItem()
        item.interface = IAdding
        item.action = 'AddContentComponent/' + self.name
        item.title = self.name
        item.permission = 'zope.ManageContent'
        self.menuitem_id = self.menu.setObject('something', item)
        component = self.getComponent()
        component.name = self.name
    activated = ContextMethod(activated)

    def deactivated(self):
        """Once activated, we have to unregister the new Content Object with
        the appropriate menu."""
        self.menu.__delitem__(self.menuitem_id)
        self.menu = None
        self.menuitem_id = None
        component = self.getComponent()
        component.name = '<component not activated>'
    deactivated = ContextMethod(deactivated)


class ContentComponentInstance(Persistent):

    implements(IContentComponentInstance)

    def __init__(self, name, schema, schemaPermissions=None):
        super(ContentComponentInstance, self).__init__()

        # Save the name of the object
        self.__name__ = name

        # XXX: We really should make a copy of the schema first, so that it
        #      cannot be changed.
        self.__schema = schema
        # Add the new attributes, if there was a schema passed in
        if schema is not None:
            for name, field in getFields(schema).items():
                setattr(self, name, field.default)
            directlyProvides(self, schema)

            # Build up a Checker rules and store it for later
            if schemaPermissions is None:
                schemaPermissions = {}
            self.__checker_getattr = PersistentDict()
            self.__checker_setattr = PersistentDict()
            for name in getFields(schema):
                get_perm, set_perm = schemaPermissions.get(name, (None, None))
                self.__checker_getattr[name] = get_perm or CheckerPublic
                self.__checker_setattr[name] = set_perm or CheckerPublic

            # Always permit our class's public methods
            self.__checker_getattr['getSchema'] = CheckerPublic


    def __setattr__(self, key, value):
        if (key in ('getSchema',) or
            key.startswith('_p_') or
            key.startswith('__') or
            key.startswith('_ContentComponentInstance__')):
            return super(ContentComponentInstance, self).__setattr__(key,
                                                                     value)

        is_schema_field = self.__schema is not None and \
                          key in getFields(self.__schema).keys()

        if is_schema_field:
            super(ContentComponentInstance, self).__setattr__(key, value)
        else:
            raise AttributeError, 'Attribute not available'


    def getSchema(self):
        return self.__schema

    def __repr__(self):
        return '<ContentComponentInstance called %s>' %self.__name__


def ContentComponentInstanceChecker(instance):
    """A function that can be registered as a Checker in defineChecker()"""
    return Checker(instance.__checker_getattr.get,
                   instance.__checker_setattr.get)

defineChecker(ContentComponentInstance, ContentComponentInstanceChecker)


