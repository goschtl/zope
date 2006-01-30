##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Skin-related Tools

$Id$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.security.proxy
from zope import viewlet
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from zope.app import zapi
from zope.app.basicskin.standardmacros import StandardMacros as BaseMacros
from zope.app.component import hooks
from zope.app.publisher.browser import BrowserView
from zope.app.publisher.interfaces.browser import IBrowserMenu

from zope.webdev import interfaces
from zope.webdev.browser import pagelet
from zope.webdev.interfaces import _

class webdev(IBrowserRequest):
    """The `webdev` layer."""


class WebDev(webdev, IDefaultBrowserLayer):
    """The `WebDev` skin."""


class StandardMacros(BaseMacros):
    macro_pages = ('main_template_macros',)


class ILeftColumn(pagelet.IPageletManager):
    """Left column pagelet manager."""


class LeftColumn(pagelet.PageletManagerBase,
                 viewlet.manager.ViewletManagerBase):
    """Ordered pagelet manager."""
    zope.interface.implements(ILeftColumn)

    def sort(self, viewlets):
        """Sort the viewlets on their weight."""
        return sorted(viewlets,
                      lambda x, y: cmp(x[1].getWeight(), y[1].getWeight()))


class MenuDropDown(object):
    """A viewlet displaying a menu"""
    zope.interface.implements(pagelet.IPagelet)

    menu_id = None

    def __init__(self, *args, **kwargs):
        super(MenuDropDown, self).__init__(*args, **kwargs)
        self.menu = zapi.getUtility(IBrowserMenu, name=self.menu_id)

    @property
    def state(self):
        return self.manager.getState(self.__name__)

    def menuItems(self):
        return self.menu.getMenuItems(self.context, self.request)

    def title(self):
        return self.menu.title

    def getWeight(self):
        return int(self.weight)

class Switch(object):
    """A browser view for the left column viewlets to expand or collapse the
    viewlet."""

    def switch(self):
        state = zope.security.proxy.removeSecurityProxy(self.context).state
        if not state.has_key('expanded'):
            state['expanded'] = False

        state['expanded'] = not state['expanded']
        return u'Ok'


class IHeaderTools(viewlet.interfaces.IViewletManager):
    """Tools that are displayed in the header."""


class HeaderTools(viewlet.manager.ViewletManagerBase):
    """Ordered viewlet."""

    def sort(self, viewlets):
        """Sort the viewlets on their weight."""
        return sorted(viewlets,
                      lambda x, y: cmp(int(x[1].weight), int(y[1].weight)))


class HelpHeaderTool(object):
    """Header tool implementing the help system."""

    title = u'Help'

    def icon_url(self):
        return zapi.getAdapter(self.request, name='help.png')()

    def url(self):
        return '++help++'


class ExitHeaderTool(object):
    """Header tool implementing the exit option."""

    title = u'Exit'

    def icon_url(self):
        return zapi.getAdapter(self.request, name='exit.png')()

    def url(self):
        site = hooks.getSite()
        url = zapi.absoluteURL(site, self.request)
        # Remove the WebDev skin, since it does not work for all of Zope 3
        url = url.replace('/++skin++WebDev', '')
        return url + '/@@SelectedManagementView.html'


class Breadcrumbs(BrowserView):
    """A custom breadcrumbs implementation"""

    def allcrumbs(self):
        result = []
        passedPackage = False
        obj = self.context
        while passedPackage is False and obj is not None:
            if interfaces.IPackage.providedBy(obj):
                passedPackage = True

            name = zapi.name(obj)
            # Special case for adding view
            if name == '+':
                name = _('Add')

            # Get the info for the current object
            info = {'name': name,
                    'url': zapi.absoluteURL(obj, self.request),
                    'icon': None}
            zmi_icon = zapi.queryMultiAdapter(
                (obj, self.request), name='zmi_icon')
            if zmi_icon:
                info['icon'] = zmi_icon()
            result.append(info)
            obj = zapi.getParent(obj)

        result.reverse()
        return result
