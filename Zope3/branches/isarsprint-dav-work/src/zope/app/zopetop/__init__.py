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

from zope.publisher.interfaces.browser import IBrowserRequest
from zope.app.rotterdam import rotterdam

class templates(IBrowserRequest):
    """Layer to store all templates."""

class images(IBrowserRequest):
    """Layer to store all images."""

class css(IBrowserRequest):
    """Layer to store all stylesheets."""

class ZopeTop(templates, images, css, rotterdam):
    """The `ZopeTop`.

    This skin consists of its three specific layers plus the rotterdam layer.
    """

