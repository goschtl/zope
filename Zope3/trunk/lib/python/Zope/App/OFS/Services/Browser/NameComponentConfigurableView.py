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
"""Generic INameComponentConfigurable view mixin

$Id: NameComponentConfigurableView.py,v 1.1 2002/12/18 20:23:03 stevea Exp $
"""

from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.ComponentArchitecture import getView
from Zope.App.Traversing import traverse
from Zope.App.PageTemplate.ViewPageTemplateFile import ViewPageTemplateFile


class NameComponentConfigurableView(BrowserView):

    indexMacros = index = ViewPageTemplateFile('NameComponentConfigurable.pt')

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
            if active:
                ob = traverse(cfg, cfg.componentPath)
                url = str(getView(ob, 'absolute_url', self.request))
            else:
                url = None
            items.append(
                {"name": name,
                 "active": active,
                 "inactive": not active,
                 "view": view,
                 "url": url
                 })

        return items

