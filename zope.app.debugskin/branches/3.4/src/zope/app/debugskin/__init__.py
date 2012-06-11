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
"""Debug skin

$Id$
"""
__docformat__ = 'restructuredtext'
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.app.rotterdam import Rotterdam

class IDebugLayer(IBrowserRequest):
    """Layer that we can register debug views with."""

class IDebugSkin(IDebugLayer, Rotterdam):
    """Rotterdam-based skin with debug functionality"""

# BBB 2006/02/18, to be removed after 12 months
try:
    import zope.app.skins
    zope.app.skins.set('Debug', IDebugSkin)
except ImportError:
    pass
