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
"""Workflow View Classes

$Id: workflows.py,v 1.2 2003/08/07 17:41:45 srichter Exp $
"""
from zope.app.browser.services.registration import \
     NameComponentRegistryView, NameRegistryView
from zope.app.traversing import traverse, getParent, getName
from zope.component import getView

class WorkflowsRegistryView(NameComponentRegistryView):

    def _getItem(self, name, view, cfg):
        item_dict = NameRegistryView._getItem(self, name, view, cfg)
        if cfg is not None:
            ob = traverse(getParent(getParent(cfg)), cfg.componentPath)
            url = str(getView(ob, 'absolute_url', self.request))
        else:
            url = None
        item_dict['url'] = url
        return item_dict
