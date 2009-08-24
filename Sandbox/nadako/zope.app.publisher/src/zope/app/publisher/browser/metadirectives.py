#############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Browser configuration code

This module defines the schemas for browser directives.

$Id$
"""
from zope.configuration.fields import GlobalObject, GlobalInterface
from zope.interface import Interface
from zope.schema import TextLine

# BBB imports
from zope.browserresource.metadirectives import (
    IBasicResourceInformation,
    IResourceDirective,
    II18nResourceDirective,
    II18nResourceTranslationSubdirective,
    IResourceDirectoryDirective,
    IIconDirective
)
from zope.browsermenu.metadirectives import (
    IMenuDirective,
    IMenuItemsDirective,
    IMenuItem,
    IMenuItemSubdirective,
    IMenuItemDirective,
    ISubMenuItemSubdirective,
    ISubMenuItemDirective,
    IAddMenuItemDirective,
)
from zope.browserpage.metadirectives import (
    IPagesDirective,
    IViewDirective,
    IViewPageSubdirective,
    IViewDefaultPageSubdirective,
    IPagesPageSubdirective,
    IPageDirective,
)


class IDefaultSkinDirective(Interface):
    """Sets the default browser skin
    """

    name = TextLine(
        title=u"Default skin name",
        description=u"Default skin name",
        required=True
        )

class IDefaultViewDirective(Interface):
    """
    The name of the view that should be the default.

    This name refers to view that should be the
    view used by default (if no view name is supplied
    explicitly).
    """

    name = TextLine(
        title=u"The name of the view that should be the default.",
        description=u"""
        This name refers to view that should be the view used by
        default (if no view name is supplied explicitly).""",
        required=True
        )

    for_ = GlobalObject(
        title=u"The interface this view is the default for.",
        description=u"""Specifies the interface for which the view is
        registered. All objects implementing this interface can make use of
        this view. If this attribute is not specified, the view is available
        for all objects.""",
        required=False
        )

    layer = GlobalInterface(
        title=u"The layer the default view is declared for",
        description=u"The default layer for which the default view is "
                    u"applicable. By default it is applied to all layers.",
        required=False
        )
