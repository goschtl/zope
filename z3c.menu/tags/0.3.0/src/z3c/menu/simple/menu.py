##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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
"""
$Id$
"""
__docformat__ = 'restructuredtext'

import zope.component
import zope.interface
from zope.contentprovider.interfaces import IContentProvider
from zope.viewlet import viewlet
from zope.app.component import hooks
from zope.app.publisher.browser import menu
from zope.app.publisher.interfaces.browser import IBrowserMenu
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.zapi import absoluteURL

from z3c.i18n import MessageFactory as _
from z3c.viewlet.manager import WeightOrderedViewletManager
from z3c.menu.simple.interfaces import ISimpleMenuItem
from z3c.menu.simple.interfaces import ITabMenu
from z3c.menu.simple.interfaces import ITab
from z3c.menu.simple.interfaces import IAction


# ISimpleMenuItem implementation
class SimpleMenuItem(viewlet.ViewletBase):
    """Selectable menu item."""

    zope.interface.implements(ISimpleMenuItem)

    template = ViewPageTemplateFile('menu_item.pt')

    selectedViewNames = None
    activeCSS = u'active-menu-item'
    inActiveCSS = u'inactive-menu-item'

    @property
    def title(self):
        return _(self.__name__)

    @property
    def url(self):
        return u''

    @property
    def extras(self):
        return {}

    @property
    def selected(self):
        name = self.__parent__.__name__
        if self.selectedViewNames is None:
            if name == self.url:
                return True
        elif name in self.selectedViewNames:
            return True
        return False

    @property
    def css(self):
        if self.selected:
            return self.activeCSS
        else:
            return self.inActiveCSS

    def render(self):
        """Return the template with the option 'menus'"""
        return self.template()


class ContextMenuItem(SimpleMenuItem):
    """Menu item viewlet generating context related links."""

    urlEndings = []
    viewURL = u''

    @property
    def selected(self):
        requestURL = self.request.getURL()
        for urlEnding in self.urlEndings:
            if requestURL.endswith(urlEnding):
                return True
        return False

    @property
    def url(self):
        contextURL = absoluteURL(self.context, self.request)
        return contextURL + '/' + self.viewURL


class GlobalMenuItem(SimpleMenuItem):
    """Menu item viewlet generating global/site related links."""

    urlEndings = []
    viewURL = u''

    @property
    def selected(self):
        requestURL = self.request.getURL()
        for urlEnding in self.urlEndings:
            if requestURL.endswith(urlEnding):
                return True
        return False

    @property
    def url(self):
        siteURL = absoluteURL(hooks.getSite(), self.request)
        return siteURL + '/' + self.viewURL


# ITabMenu implementation
class TabMenu(object):
    """Tab menu offering tabs and actions."""
    zope.interface.implements(ITabMenu)

    def __init__(self, context, request, view):
        self.__parent__ = view
        self.context = context
        self.request = request

    def update(self):
        """See zope.contentprovider.interfaces.IContentProvider"""
        self.tabs = zope.component.queryMultiAdapter(
            (self.context, self.request, self.__parent__), IContentProvider, 
            'ITab')
        if self.tabs is not None:
            self.tabs.update()
        self.actions = zope.component.queryMultiAdapter(
            (self.context, self.request, self.__parent__), IContentProvider, 
            'IAction')
        if self.actions is not None:
            self.actions.update()

    def render(self):
        """See zope.contentprovider.interfaces.IContentProvider"""
        result = u''
        if self.tabs is not None:
            result += self.tabs.render()

        if self.actions is not None:
            result += self.actions.render()

        return result


class Tab(WeightOrderedViewletManager):
    """Tab Menu"""
    zope.interface.implements(ITab)

    def render(self):
        """Return the template with the option 'menus'"""
        if not self.viewlets:
            return u''
        return self.template()


class TabItem(SimpleMenuItem):
    """Base implementation for menu items."""

    zope.interface.implements(ISimpleMenuItem)

    template = ViewPageTemplateFile('tab_item.pt')


class Action(WeightOrderedViewletManager):
    """Action Menu"""
    zope.interface.implements(IAction)

    def render(self):
        """Return the template with the option 'menus'"""
        if not self.viewlets:
            return u''
        return self.template()


class ActionItem(SimpleMenuItem):
    """Base implementation for action items."""

    zope.interface.implements(ISimpleMenuItem)

    template = ViewPageTemplateFile('action_item.pt')



class BrowserMenu(TabMenu):
    """Menu Action Menu Items

    A special tab menu, which takes its items from a browser menu
    """
    template = ViewPageTemplateFile('browser_menu_action_item.pt')
    # This is the name of the menu
    menuId = None

    def update(self):
        menu = zope.component.getUtility(IBrowserMenu, self.menuId)
        self.title = menu.title
        self.menuItems = menu.getMenuItems(self.context, self.request)

    def render(self):
        """Return the template with the option 'menus'"""
        if not self.menuItems:
            return u''
        return self.template()
