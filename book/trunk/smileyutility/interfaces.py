##############################################################################
#
# Copyright (c) 2003, 2004 Zope Corporation and Contributors.
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
"""Smiley Utility interfaces

$Id$
"""
from zope.interface import Interface
from zope.schema import Field

from zope.app.container.constraints import ContainerTypesConstraint
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.interfaces import IContainer
from zope.app.file.interfaces import IImage


class ISmileyTheme(Interface):
    """A theme is a collection of smileys having a stylistic theme.

    Themes are intened to be implemented as named utilities, which will be
    available via a local smiley service.
    """

    def getSmiley(text, request):
        """Returns a smiley for the given text and theme.

        If no smiley was found, a ComponentLookupError should be raised.
        """

    def querySmiley(text, request, default=None):
        """Returns a smiley for the given text and theme.

        If no smiley was found, the default value is returned.
        """

    def getSmileysMapping(request):
        """Return a mapping of text to URL.

        This is incredibly useful when actually attempting to substitute the
        smiley texts with a URL.
        """


class IGlobalSmileyTheme(ISmileyTheme):
    """A global smiley theme that also allows managament of smileys."""

    def provideSmiley(text, smiley_path):
        """Provide a smiley for the utility."""


class ISmiley(IImage):
    """A smiley is just a glorified image"""
    __parent__ = Field(
        constraint = ContainerTypesConstraint(ISmileyTheme))


class ILocalSmileyTheme(ISmileyTheme, IContainer):
    """A local smiley themes that manages its smileys via the container API"""

    def __setitem__(name, object):
        """Add a IMessage object."""

    __setitem__.precondition = ItemTypePrecondition(ISmiley)
