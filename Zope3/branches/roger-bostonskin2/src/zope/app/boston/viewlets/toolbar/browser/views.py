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
"""Boston skin toolbar

$Id$
"""

from zope.interface import implements

from zope.app.zapi import queryMultiAdapter

from zope.app.i18n import ZopeMessageFactory as _
from zope.app.boston.viewlets.toolbar.interfaces import IToolBarViewlet
from zope.app.publisher.browser.menu import getMenu


class ToolBarViewletManager(object):
    """Toolbar viewlet manager."""

    def macros(self, name):
        """Use macros in the template as layout components.
        
        Macros are the fastest way to render page templates, they ensure that
        everything get procesed at once in the TAL engine. Aloso offer macros
        in this implementation different layout parts where we use in different
        places, even in a iteration do we use layout macros. All this can't  be
        really done in viewlets itself. Btw, macros are a base concept for
        apply layout to different page template areas. They are developed for
        this usecase. Viewlets are used for apply the strucutre. 
        The combination of macros and viewlets is the best way I can think 
        about right now. It will offer at least a minimum of overhead and a 
        maximum of flexibility for complex structure and layout task like 
        render this nested menu structure.
        """
        return self.template.macros[name]

    def render(self):
        """See zope.contentprovider.interfaces.IContentProvider"""
        # Now render the view without the template
        return u'\n'.join([viewlet.render() for viewlet in self.viewlets])


class ToolBarViewlet(object):
    """I18n info viewlet."""

    implements(IToolBarViewlet)

    def macros(self, name):
        return self.manager.macros(name)

    def menus(self, menuId):
        return getMenu(menuId, self.context, self.request)
