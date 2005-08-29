##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Interfaces for Skin settings

$Id$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema

class ISkinSelection(zope.interface.Interface):
    """User Settings for the Skin Selection"""

    skin = zope.schema.Choice(
        title=u"Skin",
        description=u"""
            This is the skin that will be used by default.

            Note: You have to reload the page again for the setting to show an
            effect.
            """,
        vocabulary="Skins")
