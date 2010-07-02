##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""CSS for action icons.
"""

from logging import getLogger

LOG = getLogger("Action Icons CSS")

from zope.component import getUtility

from Products.Five.browser import BrowserView

from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFCore.Expression import getExprContext
from Products.CMFCore.utils import getToolByName

from Products.CMFDefault.browser.utils import memoize, ViewBase

class View(ViewBase):
    """
    CSS that dynamically checks whether Action Icons are can be used.
    Type Icons can always be used.
    """

    default_style = ".%s {/* %s */}"
    icon_style = ".%s {background: url(%s) no-repeat 0.1em}"

    def __init__(self, context, request):
        super(View, self).__init__(context, request)
        self.show_icons = self._show_icons

    @property
    @memoize
    def _show_icons(self):
        """Are action icons enabled?"""
        ptool = self._getTool('portal_properties')
        show = ptool.getProperty('enable_actionicons', False)
        if show:
            self.icon = ".icon {padding-left: 1.5em;}\n\n"
        else:
            self.icon = ".icon {padding-left: 0.5em;}\n\n"
        return show

    @property
    @memoize
    def style(self):
        """Always return a template so there are no browser errors"""
        if self.show_icons:
            return self.icon_style
        else:
            return self.default_style

    @memoize
    def actions(self):
        """List all action icons"""
        atool = self._getTool('portal_actions')
        all_actions = atool.listFilteredActionsFor(self.context)
        icons = []
        for cat in ['user', 'object', 'folder', 'workflow', 'global']:
            cat_actions = all_actions[cat]
            icons.append("/* %s actions */" % cat)
            for a in cat_actions:
                icons.append(self.style % (a['id'], a['icon']))
        return "\n\n".join(icons)

    @memoize
    def types(self):
        """List all type icons
        Type actions are always visible"""
        ttool = self._getTool('portal_types')
        types = ttool.listTypeInfo()
        econtext = getExprContext(self.context)
        icons = [self.icon_style %  (t.id,
                                  t.getIconExprObject()(econtext)) \
                for t in types]
        return "\n\n".join(icons)

    def __call__(self):
        self.request.response.setHeader("content-type", "text/css")
        self.request.response.write(self.icon)
        self.request.response.write(self.actions())
        self.request.response.write(self.types())
