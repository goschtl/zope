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

import z3c.layer.ready2go


class IReady2GoSkinLayer(z3c.layer.ready2go.IReady2GoBrowserLayer):
    """The Ready2Go skin layer offers base UI components."""


class IReady2GoBrowserSkin(IReady2GoSkinLayer):
    """The Ready2Go browser skin is accessible as named ``Ready2Go`` skin."""
