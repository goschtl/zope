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

$Id$
"""
from persistent import Persistent
from persistent.dict import PersistentDict
from zope.app import zapi
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.annotation.interfaces import IAnnotations
from zope.app.container.interfaces import IAdding
from zope.app.menu.interfaces import ILocalBrowserMenu, ILocalBrowserMenuService
from zope.app.registration.interfaces import ActiveStatus
from zope.app.container.contained import Contained
from zope.app.menu import \
     LocalBrowserMenuService, LocalBrowserMenu, LocalBrowserMenuItem
from zope.app.site.service import ServiceRegistration
from zope.app.servicenames import BrowserMenu
from zope.app.utility import UtilityRegistration
from zope.component.exceptions import ComponentLookupError
from zope.interface import directlyProvides, implements
from zope.schema import getFields
from zope.security.checker import CheckerPublic, Checker, defineChecker
from zope.security.proxy import trustedRemoveSecurityProxy

from interfaces import IContentComponentDefinition, IContentComponentMenuItem
from interfaces import IContentComponentInstance


MenuItemKey = 'http://www.zope.org/utilities/content/menuitem'


class ContentComponentDefinition(Persistent, Contained):

    implements(IContentComponentDefinition)

    def __init__(self, name=u'', schema=None, copySchema=True):
        self.name = name
        self.schema = schema
        self.copySchema = copySchema
        self.permissions = PersistentDict()
##        # This will set up the menu item entry.
##        IContentComponentMenuItem(self)
        


class ContentComponentDefinitionMenuItem(object):
    """An adapter that takes a Content Component Defintion and provides all
    necessary information to create a menu item for the content component."""

    implements(IContentComponentMenuItem)
    __used_for__ = IContentComponentDefinition

    def __init__(self, context):
        self.context = context
        ann = IAnnotations(context)
        if not ann.has_key(MenuItemKey):
            ann[MenuItemKey] = PersistentDict(
                {'interface': IAdding,
                 'title': self.context.name,
                 'description': '',
                 'permission': 'zope.ManageContent',
                 'filter_string': '',
                 'menuId': 'add_content',
                 'create': True,
                 # This is not part of the interface, but we need to store
                 # that information.
                 'menuItemId': None,
                 'menu': None}
                )
        self._data = ann[MenuItemKey]
        self._menu = self._data['menu']
        if self._menu:
            self._menuItem = self._data['menu'][self._data['menuItemId']]
        else:
            self._menuItem = None


    def _createMenuService(self):
        """Create a browser menu service for the menu item."""
        # Get the local service manager; not that we know it must exist,
        # otherwise this object would not be called.
        sm = zapi.getServices(self.context)
        # Get the default package and add a menu service called 'Menus-1'
        default = zapi.traverse(sm, 'default')
        default['Menus-1'] = LocalBrowserMenuService()
        # Register the service and set it to active
        path = "%s/default/%s" % (zapi.getPath(sm), 'Menus-1')
        reg = ServiceRegistration(BrowserMenu, path, sm)
        key = default.getRegistrationManager().addRegistration(reg)
        reg = zapi.traverse(default.getRegistrationManager(), key)
        reg.status = ActiveStatus
        return zapi.traverse(default, 'Menus-1')    


    def _createMenu(self):
        """Create a menu."""
        # Create a menu and add it to the default package
        menu = LocalBrowserMenu()
        sm = zapi.getServices(self.context)
        default = zapi.traverse(sm, 'default')
        default[self.menuId] = menu
        # Register th emenu as a utility and activate it.
        path = "%s/default/%s" % (zapi.getPath(sm), self.menuId)
        reg = UtilityRegistration(self.menuId, ILocalBrowserMenu, path)
        key = default.getRegistrationManager().addRegistration(reg)
        reg = zapi.traverse(default.getRegistrationManager(), key)
        reg.status = ActiveStatus
        return zapi.traverse(default, self.menuId)    


    def createMenuItem(self):
        "See .interfaces.IContentComponentMenuItem"
        # If 'create' is set to true, we must generate the necessary objects
        # locally
        if self.create:
            # Get the servicem manager and the default package
            sm = zapi.getServices(self.context)
            default = zapi.traverse(sm, 'default')
            service = sm.queryService(BrowserMenu)
            # Check whether the service really exists locally; if not, create
            # one for this service manager
            if (service is None or
                not ILocalBrowserMenuService.providedBy(service) or
                not zapi.name(service) in default):

                service = self._createMenuService()

            # Check whether the menu exists locally; if not create one.
            menu = service.queryInheritedMenu(self.menuId, True)
            if (menu is None or
                not ILocalBrowserMenu.providedBy(menu) or
                not zapi.name(menu) in default):

                menu = self._createMenu()

        else:
            # Find a browser menu service and make sure it is a local one.
            service = zapi.getService(self, BrowserMenu)
            if not ILocalBrowserMenuService.providedBy(service):
                raise ComponentLookupError, \
                      _('No local/peristent Browser Menu Service found.')
            # Find the browser menu and make sure it is a local one
            menu = service.queryInheritedMenu(self.menuId, True)
            if menu is None or not ILocalBrowserMenu.providedBy(menu):
                error = _('No local Browser Menu called "${name}" found.')
                error.mapping = {'name': self.menuId}
                raise ComponentLookupError, error
            
        self._data['menu'] = menu
        # Creating the menu item
        item = LocalBrowserMenuItem()
        for name in ('interface', 'action', 'title', 'description',
                     'permission', 'filter_string'):
            setattr(item, name, getattr(self, name))
        self._data['menuItemId'] = menu.addItem(item)


    def removeMenuItem(self):
        "See .interfaces.IContentComponentMenuItem"
        self._data['menu'].__delitem__(self._data['menuItemId'])
        self._data['menu'] = None
        self._data['menuItemId'] = None


    def _setMenuId(self, value):
        if self._data['menuId'] != value:
            self._data['menuId'] = value
            # This is the path of least reistence
            self.removeMenuItem()
            self.createMenuItem()

    menuId = property(lambda self: self._data['menuId'], _setMenuId)


    def _setInterface(self, value):
        if self._data['interface'] != value:
            self._data['interface'] = value
            # If a menu item exists, make sure it gets updated.
            if self._menuItem is not None:
                self._menuItem.interface = value

    interface = property(lambda self: self._data['interface'], _setInterface)


    def _getAction(self):
        return 'AddContentComponent/' + self.context.name
    
    action = property(_getAction)


    def _getTitle(self):
        return self._data['title'] or self.context.name

    def _setTitle(self, value):
        if self._data['title'] != value:
            self._data['title'] = value
            # If a menu item exists, make sure it gets updated.            
            if self._menuItem is not None:
                self._menuItem.title = value

    title = property(_getTitle, _setTitle)


    def _setDescription(self, value):
        if self._data['description'] != value:
            self._data['description'] = value
            # If a menu item exists, make sure it gets updated.
            if self._menuItem is not None:
                self._menuItem.description = value

    description = property(lambda self: self._data['description'],
                           _setDescription)

    def _setPermission(self, value):
        if self._data['permission'] != value:
            self._data['permission'] = value
            # If a menu item exists, make sure it gets updated.
            if self._menuItem is not None:
                self._menuItem.permission = value

    permission = property(lambda self: self._data['permission'],
                          _setPermission)


    def _setFilterString(self, value):
        if self._data['filter_string'] != value:
            self._data['filter_string'] = value
            # If a menu item exists, make sure it gets updated.
            if self._menuItem is not None:
                self._menuItem.filter = value

    filter_string = property(lambda self: self._data['filter_string'],
                             _setFilterString)


    def _setCreate(self, value):
        if self._data['create'] != value:
            self.removeMenuItem()
            self._data['create'] = value
            self.createMenuItem()

    create = property(lambda self: self._data['create'],
                      _setCreate)



class ContentComponentDefinitionRegistration(UtilityRegistration):
    """Content Component Registration"""

    def activated(self):
        """Once activated, we have to register the new Content Object with the
        appropriate menu.
        """
        component = self.getComponent()
        component = trustedRemoveSecurityProxy(component)
        component.name = self.name
        IContentComponentMenuItem(component).createMenuItem()

    def deactivated(self):
        """Once activated, we have to unregister the new Content Object with
        the appropriate menu."""
        component = self.getComponent()
        component = trustedRemoveSecurityProxy(component)
        component.name = None
        IContentComponentMenuItem(component).removeMenuItem()


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
            raise AttributeError, 'Attribute "%s" not available' %key


    def getSchema(self):
        return self.__schema


    def __repr__(self):
        return '<ContentComponentInstance called %s>' %self.__name__



def ContentComponentInstanceChecker(instance):
    """A function that can be registered as a Checker in defineChecker()"""
    return Checker(instance.__checker_getattr.get,
                   instance.__checker_setattr.get)

defineChecker(ContentComponentInstance, ContentComponentInstanceChecker)
