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

$Id: NameConfigurableView.py,v 1.4 2002/12/21 20:05:46 stevea Exp $
"""

from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.ComponentArchitecture import getView
from Zope.App.PageTemplate.ViewPageTemplateFile import ViewPageTemplateFile

class NameConfigurableView(BrowserView):

    indexMacros = index = ViewPageTemplateFile('NameConfigurable.pt')

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

