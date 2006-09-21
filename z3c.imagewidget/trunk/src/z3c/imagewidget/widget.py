##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Image Widget Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface
from zope.schema import fieldproperty

import z3c.sessionwidget
from z3c.imagewidget import interfaces

class ImageInputWidget(z3c.sessionwidget.SessionInputWidget):
    """Image input widget."""
    zope.interface.implements(interfaces.IImageWidget)

    width = fieldproperty.FieldProperty(interfaces.IImageWidget['width'])
    height = fieldproperty.FieldProperty(interfaces.IImageWidget['height'])
