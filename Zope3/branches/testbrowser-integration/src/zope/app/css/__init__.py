##############################################################################
#
# Copyright (c) 2002 - 2005 Zope Corporation and Contributors.
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
"""Prototyping skin called `CSS` 

$Id$
"""
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.app.rotterdam import Rotterdam


class layer(IBrowserRequest):
    """A clean ILayer called `zope.app.css.layer` used in `CSS` skin."""


class CSS(layer, Rotterdam):
    """The `CSS` skin based on the Rotterdam skin.

    It is available via `++skin++zope.app.css.CSS`
    or via `++skin++CSS`.
    """
