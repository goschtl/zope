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
"""Local Menu Service

$Id: menu.py,v 1.3 2003/08/16 15:32:40 srichter Exp $
"""
__metaclass__ = type 

from persistence import Persistent
from zope.app import zapi
from zope.app.component.nextservice import getNextService
from zope.app.container.ordered import OrderedContainer
from zope.app.interfaces.services.menu import \
     ILocalBrowserMenu, ILocalBrowserMenuService
from zope.app.interfaces.publisher.browser import \
     IBrowserMenuItem, IGlobalBrowserMenuService
from zope.app.interfaces.services.service import ISimpleService
from zope.app.publisher.browser.globalbrowsermenuservice import \
     Menu, BaseBrowserMenuService
from zope.app.services.servicenames import Utilities, BrowserMenu
from zope.interface import implements
from zope.component.exceptions import ComponentLookupError
from zope.context import ContextMethod
from zope.interface import providedBy
from zope.security.proxy import trustedRemoveSecurityProxy


class LocalBrowserMenuItem(Persistent):
    """A persistent browser menu item."""

    implements(IBrowserMenuItem)

    # See zope.app.interfaces.publisher.browser.IBrowserMenuItem
    interface = None

    # See zope.app.interfaces.publisher.browser.IBrowserMenuItem
    action = u''

    # See zope.app.interfaces.publisher.browser.IBrowserMenuItem
    title = u''

    # See zope.app.interfaces.publisher.browser.IBrowserMenuItem
    description = u''

    # See zope.app.interfaces.publisher.browser.IBrowserMenuItem
    permission = None

    # See zope.app.interfaces.publisher.browser.IBrowserMenuItem
    filter_string = u''
    

class LocalBrowserMenu(OrderedContainer):
    """A persistent browser menu that can store menu item objects."""
    
    implements(ILocalBrowserMenu)

    # See zope.app.interfaces.publisher.browser.IBrowserMenu
    title = u''

    # See zope.app.interfaces.publisher.browser.IBrowserMenu
    description = u''

    # See zope.app.interfaces.publisher.browser.IBrowserMenu
    usage = u''

    # See zope.app.interfaces.publisher.browser.IBrowserMenu
    inherit = True

    def __init__(self):
        super(LocalBrowserMenu, self).__init__()
        self._next = 0

    def getMenuItems(self, object=None):
        """See zope.app.interfaces.publisher.browser.IBrowserMenu"""
        result = []
        interfaces = list(providedBy(object).flattened())
        for menuitem in self.values():
            if menuitem.interface in interfaces or object is None:
                result.append(
                    (menuitem.action,
                     menuitem.title,
                     menuitem.description,
                     menuitem.filter_string or None,
                     menuitem.permission))

        return result

    def setObject(self, key, object):
        """See zope.app.interfaces.container.Container"""
        self._next += 1
        key = str(self._next)
        while key in self:
            self._next += 1
            key = str(self._next)
        super(LocalBrowserMenu, self).setObject(key, object)
        return key


class LocalBrowserMenuService(BaseBrowserMenuService, Persistent):
    """This implementation strongly depends on the semantics of
    GlobalBrowserMenuService."""
    
    implements(ILocalBrowserMenuService, ISimpleService)

    def __init__(self):
        super(LocalBrowserMenuService, self).__init__()


    def getAllLocalMenus(self):
        """See zope.app.interfaces.publisher.browser.IBrowserMenuService"""
        utilities = zapi.getService(self, Utilities)
        matching = utilities.getRegisteredMatching(ILocalBrowserMenu)
        return map(lambda m: m[2].active().getComponent(), matching)
    getAllLocalMenus = ContextMethod(getAllLocalMenus)


    def getLocalMenu(self, menu_id):
        """See zope.app.interfaces.services.menu.ILocalBrowserMenuService"""
        menu = self.queryLocalMenu(menu_id)
        if menu is None:
            raise ComponentLookupError(menu_id)
        return menu
    getLocalMenu = ContextMethod(getLocalMenu)


    def queryLocalMenu(self, menu_id, default=None):
        """See zope.app.interfaces.services.menu.ILocalBrowserMenuService"""
        utilities = zapi.getService(self, Utilities)
        matching = utilities.getRegisteredMatching(ILocalBrowserMenu, menu_id)
        if matching and matching[0][2].active():
            return matching[0][2].active().getComponent()
        return default
    queryLocalMenu = ContextMethod(queryLocalMenu)


    def getInheritedMenu(self, menu_id, canBeLocal=False):
        """See zope.app.interfaces.services.menu.ILocalBrowserMenuService"""
        menu = self.queryInheritedMenu(menu_id, canBeLocal)
        if menu is None:
            raise ComponentLookupError(menu_id)
        return menu
    getInheritedMenu = ContextMethod(getInheritedMenu)


    def queryInheritedMenu(self, menu_id, canBeLocal=False, default=None):
        """See zope.app.interfaces.services.menu.ILocalBrowserMenuService"""
        if canBeLocal and self.queryLocalMenu(menu_id):
            return self.queryLocalMenu(menu_id)
        # Another service (global) should always be available
        next = getNextService(self, BrowserMenu)

        # Check whether we deal with a Global Menu Service
        if IGlobalBrowserMenuService.isImplementedBy(next):
            return next._registry.get(menu_id, default)

        return next.queryInheritedMenu(menu_id, True, default)        
    queryInheritedMenu = ContextMethod(queryInheritedMenu)


    def getAllMenuItems(self, menu_id, object):
        """See zope.app.interfaces.publisher.browser.IBrowserMenuService"""
        result = []
    
        # Find the local items, if available 
        menu = self.queryLocalMenu(menu_id)
        if menu is not None:
            result += menu.getMenuItems(object)
            # We might not want to inherit menu entries from higher up
            if not menu.inherit:
                return result
    
        # Try to find the next service and get its items. The next service is
        # also responsible for finding items higher up.
        next = getNextService(self, BrowserMenu)
        result += next.getAllMenuItems(menu_id, object)

        return tuple(result)
    getAllMenuItems = ContextMethod(getAllMenuItems)


    def getMenu(self, menu_id, object, request, max=999999):
        """See zope.app.interfaces.publisher.browser.IBrowserMenuService"""
        return zapi.ContextSuper(LocalBrowserMenuService,
                     self).getMenu(menu_id, object, request, max)
    getMenu = ContextMethod(getMenu)


    def getFirstMenuItem(self, menu_id, object, request):
        """See zope.app.interfaces.publisher.browser.IBrowserMenuService"""
        return zapi.ContextSuper(LocalBrowserMenuService,
                     self).getFirstMenuItem(menu_id, object, request)
    getFirstMenuItem = ContextMethod(getFirstMenuItem)


    def getMenuUsage(self, menu_id):
        """See zope.app.interfaces.publisher.browser.IBrowserMenuService"""
        return self.getInheritedMenu(menu_id, True).usage
    getMenuUsage = ContextMethod(getMenuUsage)

