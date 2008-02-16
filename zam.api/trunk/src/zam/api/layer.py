##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
$Id: __init__.py 97 2007-03-29 22:58:27Z rineichen $
"""

from zope.viewlet.interfaces import IViewletManager
from z3c.menu.ready2go import interfaces
import z3c.layer.ready2go


class IZAMBrowserLayer(z3c.layer.ready2go.IReady2GoBrowserLayer):
    """Secure browser layer used for ZAM."""


# ZAM viewlet manager
class ICSS(IViewletManager):
    """CSS viewlet manager."""


class IJavaScript(IViewletManager):
    """JavaScript viewlet manager."""


class IBreadcrumb(IViewletManager):
    """Breadcrumb viewlet manager."""


class ISideBar(IViewletManager):
    """SideBar viewlet manager."""
