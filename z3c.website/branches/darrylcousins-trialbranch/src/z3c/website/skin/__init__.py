##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Resource License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: __init__.py 40 2007-02-21 09:18:28Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

from zope.app.component import hooks
from zope.publisher.browser import BrowserPage
from zope.traversing.browser import absoluteURL
from zope.viewlet.interfaces import IViewletManager
from zope.viewlet import viewlet

import z3c.layer.pagelet
import z3c.website.layer


InterfaceJavaScriptViewlet = viewlet.JavaScriptViewlet('interface.js')
JQueryCornerJavaScriptViewlet = viewlet.JavaScriptViewlet('jquery.corner.js')
DemoJavaScriptViewlet = viewlet.JavaScriptViewlet('demo.js')
DemoCSSViewlet = viewlet.CSSViewlet('demo.css')


class IWebSiteBrowserSkin(z3c.layer.pagelet.IPageletBrowserLayer, 
    z3c.website.layer.IWebSiteBrowserLayer):
    """The ``Z3CWebSite`` browser skin."""


class IToolManager(IViewletManager):
    """Manager for tool viewlets."""


class SiteURL(BrowserPage):

    def __call__(self):
        return absoluteURL(hooks.getSite(), self.request)
