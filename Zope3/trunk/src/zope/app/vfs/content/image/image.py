##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""VFS Image Add View

$Id: image.py,v 1.3 2002/12/30 14:03:21 stevea Exp $
"""
from zope.publisher.vfs import VFSView

from zope.app.event import publish
from zope.app.event.objectevent import ObjectCreatedEvent

from zope.app.interfaces.container import IAdding
from zope.app.content.image import Image


class ImageAdd(VFSView):
    "Provide a user interface for adding a Image content object"

    __used_for__ = IAdding

    def __call__(self, mode, instream, start):
        content = Image()
        try:
            instream.seek(start)
        except:
            pass
        content.setData(instream.read())

        publish(self.context, ObjectCreatedEvent(content))
        return self.context.add(content)
