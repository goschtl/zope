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
"""VFS Folder Add View

$Id: FolderAdd.py,v 1.1 2002/12/20 10:31:47 srichter Exp $
"""
from Zope.Publisher.VFS.VFSView import VFSView

from Zope.Event import publish
from Zope.Event.ObjectEvent import ObjectCreatedEvent

from Zope.App.OFS.Container.IAdding import IAdding
from Zope.App.OFS.Content.Folder.Folder import Folder


class FolderAdd(VFSView):
    "Provide a user interface for adding a Folder content object"

    __used_for__ = IAdding

    def __call__(self):
        "Add a folder"
        content = Folder()
        publish(self.context, ObjectCreatedEvent(content))
        return self.context.add(content)

