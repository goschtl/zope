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
$Id: layer.py 197 2007-04-13 05:03:32Z rineichen $
"""

import zope.component
from zope.contentprovider.interfaces import IContentProvider
from zope.traversing.interfaces import IContainmentRoot
from zope.traversing import api
from zope.viewlet.interfaces import IViewletManager
from zope.app.component import hooks

import z3c.pagelet.interfaces
import z3c.form.interfaces
from z3c.menu.ready2go import item

from zam.api import interfaces


class IAddMenu(IContentProvider):
    """Add menu item controlling tab."""


class IGlobalMenu(IViewletManager):
    """Global menu item controlling tab."""


class ISiteMenu(IViewletManager):
    """Site menu item controlling tab."""


class IContextMenu(IViewletManager):
    """Context menu item controlling tab."""


# default ZAM root menu item
class RootMenuItem(item.GlobalMenuItem):
    """Zope root menu item."""

    viewName = 'contents.html'
    viewInterface = interfaces.IRootMenuItemPage
    weight = 1


class ZAMRootPluginsMenuItem(item.GlobalMenuItem):
    """Zope root menu item."""

    viewName = 'plugins.html'
    viewInterface = interfaces.IRootMenuItemPage
    weight = 1


class ContentsMenuItem(item.ContextMenuItem):
    """ZAM global contents.html menu item."""

    viewName = 'contents.html'
    viewInterface = interfaces.IRootMenuItemPage
    weight = 1


class PluginsMenuItem(item.ContextMenuItem):
    """ZAM site plugins menu item."""

    viewName = 'plugins.html'
    viewInterface = interfaces.IPluginManagement
    weight = 100
