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

$Id: folder.py,v 1.3 2002/12/30 14:03:20 stevea Exp $
"""
from zope.publisher.vfs import VFSView

from zope.app.event import publish
from zope.app.event.objectevent import ObjectCreatedEvent

from zope.app.interfaces.container import IAdding
from zope.app.content.folder import Folder


class FolderAdd(VFSView):
    "Provide a user interface for adding a Folder content object"

    __used_for__ = IAdding

    def __call__(self):
        "Add a folder"
        content = Folder()
        publish(self.context, ObjectCreatedEvent(content))
        return self.context.add(content)



"""VFS-View for IFolder

$Id: folder.py,v 1.3 2002/12/30 14:03:20 stevea Exp $
"""
import datetime
zerotime = datetime.datetime.fromtimestamp(0)

from zope.component import getAdapter
from zope.app.interfaces.dublincore import IZopeDublinCore
from zope.app.vfs.container.view import \
     VFSContainerView

class FolderView(VFSContainerView):
    """Specific Folder VFS view."""

    __implments__ = VFSContainerView.__implements__

    _directory_type = 'Folder'

    def _getServiceManagerStat(self):
        """Get the stat information of the local service manager."""
        # XXX ServiceManager does not use the DublinCore to keep track of its
        # creation and modification times, so we use the data of the Folder
        # right now.
        dc = getAdapter(self.context, IZopeDublinCore)
        if dc is not None:
            created = dc.created
            modified = dc.modified
        else:
            created = zerotime
            modified = zerotime
        if modified is None:
            modified = created
        dir_mode = 16384 + 504
        uid = "nouser"
        gid = "nogroup"
        return (dir_mode, 0, 0, 0, uid, gid, 4096, modified, modified,
                created)


    def exists(self, name):
        'See IVFSDirectoryPublisher'
        if self.context.hasServiceManager() and name == '++etc++Services':
            return True
        return super(FolderView, self).exists(name)


    def listdir(self, with_stats=0, pattern='*'):
        'See IVFSDirectoryPublisher'
        result = super(FolderView, self).listdir(with_stats, pattern)
        if self.context.hasServiceManager():
            result = [('++etc++Services', self._getServiceManagerStat())] \
                     + result
        return result
