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
$Id: __init__.py 72088 2007-01-18 01:09:33Z rogerineichen $
"""
__docformat__ = "reStructuredText"

from zope.viewlet.interfaces import IViewletManager

import z3c.layer.ready2go


class IReady2GoBrowserSkin(z3c.layer.ready2go.IReady2GoBrowserLayer):
    """The Ready2Go skin is not registered by default. 
    
    This could be done in your project or inherit from this layer and
    register your own.
    
    """


class ICSS(IViewletManager):
    """CSS viewlet manager."""


class IJavaScript(IViewletManager):
    """JavaScript viewlet manager."""


class IBreadcrumb(IViewletManager):
    """Breadcrumb viewlet manager."""


class IGlobalMenu(IViewletManager):
    """GlobalMenu viewlet manager."""


class IContextMenu(IViewletManager):
    """ContextMenu viewlet manager."""


class ISideBar(IViewletManager):
    """SideBar viewlet manager."""
