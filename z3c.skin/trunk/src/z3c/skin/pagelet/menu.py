##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
__docformat__ = "reStructuredText"

import zope.interface
from zope.app.component import hooks
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.traversing import browser

import z3c.viewlet.manager
from z3c.menu.simple import menu

from z3c.skin.pagelet import interfaces


class GlobalMenu(z3c.viewlet.manager.WeightOrderedViewletManager):
    """Tab Menu"""
    zope.interface.implements(interfaces.IGlobalMenu)

    def render(self):
        """Return the template with the option 'menus'"""
        if not self.viewlets:
            return u''
        return self.template()


class ContextMenu(z3c.viewlet.manager.WeightOrderedViewletManager):
    """Tab Menu"""
    zope.interface.implements(interfaces.IContextMenu)

    def render(self):
        """Return the template with the option 'menus'"""
        if not self.viewlets:
            return u''
        return self.template()


class TabMenuItem(menu.SimpleMenuItem):

    template = ViewPageTemplateFile('menu_tab_item.pt')


    def url(self):
        baseURL = browser.absoluteURL(self.context, self.request)
        return baseURL + '/' + self.viewURL
