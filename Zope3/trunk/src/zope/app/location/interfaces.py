##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Location framework interfaces

$Id$
"""
from zope.interface import Interface, Attribute
from zope import schema

class ILocation(Interface):
    """Objects that have a structural location"""

    __parent__ = Attribute("The parent in the location hierarchy")

    __name__ = schema.TextLine(
        title=u"The name within the parent",
        description=u"The parent can be traversed with this name to "
                    u"get the object."
        )
