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
"""Smiley Configuration interfaces

$Id: metadirectives.py,v 1.1 2003/08/22 21:27:33 srichter Exp $
"""
from zope.interface import Interface
from zope.configuration.fields import Path
from zope.schema import TextLine

class IThemeDirective(Interface):
    """Define a new theme."""
    
    name = TextLine(
        title=u"Theme Name",
        description=u"The name of the theme.",
        default=None,
        required=False)

class ISmileySubdirective(Interface):
    """This directive adds a new smiley using the theme information of the
    complex smileys directive."""

    text = TextLine(
        title=u"Smiley Text",
        description=u"The text that represents the smiley, i.e. ':-)'",
        required=True)

    file = Path(
        title=u"Image file",
        description=u"Path to the image that represents the smiley.",
        required=True)

class ISmileyDirective(ISmileySubdirective):
    """This is a standalone directive registering a smiley for a certain
    theme."""

    theme = TextLine(
        title=u"Theme",
        description=u"The theme the smiley belongs to.",
        default=None,
        required=False)

class IDefaultThemeDirective(IThemeDirective):
    """Specify the default theme."""
