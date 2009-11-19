##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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

import zope.schema
from zope.contentprovider.interfaces import IContentProvider
from zope.viewlet.interfaces import IViewletManager
from zope.viewlet.interfaces import IViewlet

from z3c.i18n import MessageFactory as _


class ISimpleMenuItem(IViewlet):
    """Simple menu item."""

    title = zope.schema.TextLine(
        title=_(u'Title'),
        description=_(u'The menu title.'),
        default=u'',
        readonly=True,
        required=False)

    url = zope.schema.TextLine(
        title=_(u'URL'),
        description=_(u'The url the menu points to.'),
        default=u'',
        readonly=True,
        required=False)

    extras = zope.schema.Dict(
        title=_(u'Extras'),
        description=_(u'Extra values usefull for custom attributes.'),
        key_type=zope.schema.TextLine(title=u'Key'),
        value_type=zope.schema.TextLine(title=u'Value')
        )

    selected = zope.schema.Bool(
        title=_(u"Required"),
        default=False,
        required=False)

    css = zope.schema.TextLine(
        title=_(u'CSS'),
        description=_(u'The css class depending on the selected stati.'),
        default=u'',
        readonly=True,
        required=False)


class ITabMenu(IContentProvider):
    """Tab Menu

    Items in this menu directly releat to the context you are viewing. In
    general, the tab menu consists of two sub-menus, the tabs and the
    actions.
    """


class ITab(IViewletManager):
    """Menu controlling tab items."""


class ITabItem(ISimpleMenuItem):
    """Tab menu item."""


class IAction(IViewletManager):
    """Menu controlling the action items."""


class ITabItem(ISimpleMenuItem):
    """Action menu item."""
