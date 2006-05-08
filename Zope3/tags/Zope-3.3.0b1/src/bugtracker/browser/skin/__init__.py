##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Bug tracker skin

$Id$
"""
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.app.rotterdam import Rotterdam

class IBugtrackerLayer(IBrowserRequest):
    """Layer for registering bugtracker views"""

class IBugtrackerSkin(IBugtrackerLayer, Rotterdam):
    """The bugtracker skin"""

# BBB 2006/02/18, to be removed after 12 months
import zope.app.skins
zope.app.skins.set('tracker', IBugtrackerSkin)
