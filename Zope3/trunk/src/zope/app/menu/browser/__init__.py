##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Menu Access and Local Menu Service Views

$Id$
"""
from zope.interface import implements
from zope.app import zapi
from zope.app.container.browser.contents import Contents
from zope.app.component.localservice import queryNextService
from zope.app.dublincore.interfaces import IZopeDublinCore
from zope.app.menu.interfaces import ILocalBrowserMenu
from zope.app.servicenames import Utilities, BrowserMenu


class MenuContents(Contents):

    def _extractContentInfo(self, item):
        id, obj = item
        info = {}
        info['cb_id'] = info['id'] = id
        info['object'] = obj

        info['url'] = id
        info['title'] = obj.title
        info['action'] = obj.action

        dc = IZopeDublinCore(obj, None)
        if dc is not None:

            formatter = self.request.locale.dates.getFormatter(
                'dateTime', 'short')
            created = dc.created
            if created is not None:
                info['created'] = formatter.format(created)

            modified = dc.modified
            if modified is not None:
                info['modified'] = formatter.format(modified)

        return info


class BrowserMenuServiceOverview:

    def getLocalMenus(self):
        menus_info = []
        utilities = zapi.getService(Utilities)
        for menu_id, menu in utilities.getLocalUtilitiesFor(ILocalBrowserMenu):
            menus_info.append(self._getInfoFromMenu(menu_id, menu))
        return menus_info


    def getInheritedMenus(self):
        menus = []
        utilities = queryNextService(self.context, Utilities)
        for id, menu in utilities.getUtilitiesFor(ILocalBrowserMenu):
            menus.append(self._getInfoFromMenu(id, menu))
        # Global Browser Menus
        service = zapi.getGlobalService(BrowserMenu)
        for id, menu in service._registry.items():
            menus.append(self._getInfoFromMenu(id, menu))
        return menus


    def _getInfoFromMenu(self, menu_id, menu):
        info = {}
        info['id'] = menu_id
        info['title'] = menu.title
        info['local_items'] = self._getItemsInfo(menu)
        info['inherit'] = False
        if getattr(menu, 'inherit', False):
            info['inherit'] = True
            next = queryNextService(menu, BrowserMenu)
            if next is not None:
                try:
                    inherit_menu = next.queryLocalMenu(menu_id)
                except AttributeError:
                    # We deal with a global broqwser menu service
                    inherit_menu = next._registry.get(menu_id, None)

                if not inherit_menu:
                    info['inherited_items'] = []
                else:
                    info['inherited_items'] = self._getItemsInfo(inherit_menu)
        else:
            info['inherited_items'] = None
        return info


    def _getItemsInfo(self, menu):
        menu_items = []

        for items in menu.getMenuItems():
            action, title, description, filter, permission = items

            menu_items.append({'title': title,
                               'action': action})
        return menu_items
