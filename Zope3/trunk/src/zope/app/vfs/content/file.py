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
"""VFS File Add View

$Id: file.py,v 1.3 2002/12/30 14:03:20 stevea Exp $
"""
from zope.publisher.vfs import VFSView

from zope.app.event import publish
from zope.app.event.objectevent import ObjectCreatedEvent

from zope.app.interfaces.container import IAdding
from zope.app.content.file import File


class FileAdd(VFSView):
    "Provide a user interface for adding a File content object"

    __used_for__ = IAdding

    def __call__(self, mode, instream, start):
        "Add a contact"
        content = File()
        try:
            instream.seek(start)
        except:
            pass
        content.setData(instream.read())

        publish(self.context, ObjectCreatedEvent(content))
        return self.context.add(content)



"""VFS-View for IFile

VFS-view implementation for a generic file.

$Id: file.py,v 1.3 2002/12/30 14:03:20 stevea Exp $
"""
from zope.publisher.vfs import VFSFileView

class FileView(VFSFileView):

    def _setData(self, data):
        self.context.setData(data)

    def _getData(self):
        return self.context.getData()

    def _getSize(self):
        return self.context.getSize()
