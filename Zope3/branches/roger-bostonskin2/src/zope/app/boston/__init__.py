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
"""Boston ZMI

$Id$
"""

from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.viewlet import manager
from zope.viewlet import viewlet
from zope.viewlet.interfaces import IViewletManager


class boston(IBrowserRequest):
    """The `boston` layer."""

class Boston(boston, IDefaultBrowserLayer):
    """The `Boston` skin.

    It is available via `++skin++zope.app.boston.Boston`
    or via `++skin++Boston`.
    """


class IHead(IViewletManager):
    """Head viewlet manager."""


class ICSS(IViewletManager):
    """CSS viewlet manager."""


class IJavaScript(IViewletManager):
    """JavaScript viewlet manager."""


class IToolBar(IViewletManager):
    """Toolbar viewlet manager."""


class ILeft(IViewletManager):
    """Left viewlet manager."""


class LeftViewletManager(manager.ViewletManagerBase):
    """Ordered viewlet."""

    def sort(self, viewlets):
        """Sort the viewlets on their weight."""
        return sorted(viewlets, lambda x, y: cmp(x[1].getWeight(), y[1].getWeight()))


class OrderedViewlet(viewlet.ViewletBase):
    """Ordered viewlet."""

    def getWeight(self):
        """REturns the weight of the viewlet."""
        return int(self.weight)


BostonSkinCSSViewlet = viewlet.CSSViewlet('skin.css', 'all')

BostonWidgetCSSViewlet = viewlet.CSSViewlet('widget.css', 'all')

BostonXMLTreeCSSViewlet = viewlet.CSSViewlet('xmltree.css', 'all')

BostonToolBarCSSViewlet = viewlet.CSSViewlet('toolbar.css', 'all')

BostonJavascriptViewlet = viewlet.JavaScriptViewlet('boston.js')

BostonXMLTreeJavaScriptViewlet = viewlet.JavaScriptViewlet('xmltree.js')
