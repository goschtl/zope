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

$Id: NameComponentConfigurableView.py,v 1.2 2002/12/21 20:05:46 stevea Exp $
"""

from Zope.App.Traversing import traverse
from Zope.App.PageTemplate.ViewPageTemplateFile import ViewPageTemplateFile
from Zope.App.OFS.Services.Browser.NameConfigurableView \
        import NameConfigurableView
from Zope.ComponentArchitecture import getView

class NameComponentConfigurableView(NameConfigurableView):

    indexMacros = index = ViewPageTemplateFile('NameComponentConfigurable.pt')

    def _getItem(self, name, view, cfg):
        item_dict = NameConfigurableView._getItem(self, name, view, cfg)
        if cfg is not None:
            ob = traverse(cfg, cfg.componentPath)
            url = str(getView(ob, 'absolute_url', self.request))
        else:
            url = None
        item_dict['url'] = url
        return item_dict

