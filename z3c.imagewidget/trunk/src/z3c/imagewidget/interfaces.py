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
"""Image Widget Interfaces

$Id$
"""
__docformat__ = "reStructuredText"
import zope.schema

from zope.app.form.browser import interfaces
from zope.app.i18n import ZopeMessageFactory as _


class IImageWidget(interfaces.IBrowserWidget):
    """A widget for inputting and displaying images."""

    width = zope.schema.Int(
        title=_(u'Width'),
        description=_(u'The width of the image is to be rendered or '
                      u'sized to.'),
        required=False,
        missing_value=None)

    height = zope.schema.Int(
        title=_(u'Height'),
        description=_(u'The height of the image is to be rendered or '
                      u'sized to.'),
        required=False,
        missing_value=None)
