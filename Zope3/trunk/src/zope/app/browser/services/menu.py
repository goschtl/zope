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
"""Local Menu Service Views

$Id: menu.py,v 1.5 2003/08/25 14:14:06 sidnei Exp $
"""

from zope.app import zapi
from zope.app.browser.container.contents import Contents
from zope.app.component.nextservice import queryNextService
from zope.app.interfaces.dublincore import IZopeDublinCore
from zope.app.interfaces.services.menu import ILocalBrowserMenu
from zope.app.services.servicenames import Utilities, BrowserMenu
from zope.security.proxy import trustedRemoveSecurityProxy

class MenuContents(Contents):

    def _extractContentInfo(self, item):
        id, obj = item
        info = {}
        info['cb_id'] = info['id'] = id
        info['object'] = obj

        info['url'] = id
        info['title'] = obj.title
        info['action'] = obj.action

        dc = zapi.queryAdapter(obj, IZopeDublinCore)
        if dc is not None:

            formatter = self.request.locale.getDateTimeFormatter('short')
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
        utilities = zapi.getService(self.context, Utilities)
        for menu_id, menu in utilities.getLocalUtilitiesFor(ILocalBrowserMenu):
            menus_info.append(self._getInfoFromMenu(menu_id, menu))
        return menus_info


    def getInheritedMenus(self):
        menus = []
        utilities = queryNextService(self.context, Utilities)
        for id, menu in utilities.getUtilitiesFor(ILocalBrowserMenu):
            menus.append(self._getInfoFromMenu(id, menu))
        # Global Browser Menus
        service = zapi.getService(None, BrowserMenu)
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
