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

from zope.viewlet.interfaces import IViewletManager

from z3c.skin.pagelet import layer


class IPageletBrowserSkin(layer.IPageletBrowserLayer):
    """The ``Z3CPageletDemo`` application skin."""


class ITitle(IViewletManager):
    """Title viewlet manager."""


class ICSS(IViewletManager):
    """CSS viewlet manager."""


class IJavaScript(IViewletManager):
    """JavaScript viewlet manager."""


class IBreadcrumb(IViewletManager):
    """Breadcrumb viewlet manager."""


class INavigation(IViewletManager):
    """Navigation viewlet manager."""


class IMenu(IViewletManager):
    """Menu viewlet manager."""


class ITab(IViewletManager):
    """Tab viewlet manager."""
