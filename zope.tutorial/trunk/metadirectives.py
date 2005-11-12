##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Schema for the ``zope:tutorial`` directive

$Id: $
"""
__docformat__ = 'restructuredtext'

import zope.interface
import zope.schema
from zope.configuration import fields

class ITutorialDirective(zope.interface.Interface):
    """Register a new Tutorial"""

    name = zope.schema.BytesLine(
        title=u"Tutrial Name",
        description=u"Name of the tutorial as it will appear in the URL.",
        required=True)

    title = fields.MessageID(
        title=u"Title",
        description=u"Provides a title for the chapter.",
        required=True)

    path = fields.Path(
        title=u"Path to File",
        description=u"Path to the file that contains the tutorial content.",
        required=False)
