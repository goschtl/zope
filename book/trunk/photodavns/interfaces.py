##############################################################################
#
# Copyright (c) 2003, 2004 Zope Corporation and Contributors.
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
"""IPhoto WebDAV namespace related interfaces.

$Id: interfaces.py,v 1.1.1.1 2004/02/18 18:07:08 srichter Exp $
"""
from zope.interface import Interface
from zope.schema import Text, TextLine, Int, Float

photodavns = "http://namespaces.zope.org/dav/photo/1.0"

class IPhoto(Interface):
    """A WebDAV namespace to store photo-related meta data.

    The 'IPhoto' schema/namespace can be used in WebDAV clients to determine
    information about a particular picture. Obviously, this namespace makes
    only sense on Image objects.
    """

    height = Int(
        title=u"Height",
        description=u"Specifies the height in pixels.",
        min=1)

    width = Int(
        title=u"Width",
        description=u"Specifies the width in pixels.",
        min=1)

    equivalent35mm = TextLine(
        title=u"35mm equivalent",
        description=u"The photo's size in 35mm is equivalent to this amount")

    aperture = TextLine(
        title=u"Aperture",
        description=u"Size of the aperture.")

    exposureTime = Float(
        title=u"Exposure Time",
        description=u"Specifies the exposure time in seconds.")
