##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""`ZopeTop` skin package.

$Id$
"""
__docformat__ = "reStructuredText"

from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.app.rotterdam import Rotterdam

class templates(IBrowserRequest):
    """Layer to store all templates."""

class images(IBrowserRequest):
    """Layer to store all images."""

class css(IBrowserRequest):
    """Layer to store all stylesheets."""

class ZopeTop(templates, images, css, Rotterdam):
    """The `ZopeTop`.

    This skin consists of its three specific layers plus the rotterdam layer.
    """

# BBB 2006/02/18, to be removed after 12 months
import zope.app.skins
zope.app.skins.set('ZopeTop', ZopeTop)
