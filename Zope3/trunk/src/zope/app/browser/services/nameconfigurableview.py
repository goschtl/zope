##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Generic INameConfigurable view mixin

$Id: nameconfigurableview.py,v 1.2 2002/12/25 14:12:36 jim Exp $
"""

from zope.publisher.browser import BrowserView
from zope.component import getView
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

class NameConfigurableView(BrowserView):

    indexMacros = index = ViewPageTemplateFile('nameconfigurable.pt')

    def update(self):

        names = list(self.context.listConfigurationNames())
        names.sort()

        items = []
        for name in names:
            registry = self.context.queryConfigurations(name)
            view = getView(registry, "ChangeConfigurations", self.request)
            view.setPrefix(name)
            view.update()
            cfg = registry.active()
            active = cfg is not None
            items.append(self._getItem(name, view, cfg))

        return items

    def _getItem(self, name, view, cfg):
        # hook for subclasses. returns a dict to append to an item
        return {"name": name,
                "active": cfg is not None,
                "inactive": cfg is None,
                "view": view,
                }
