##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""VFS-View for IFolder

$Id: FolderView.py,v 1.2 2002/12/23 08:15:36 srichter Exp $
"""
import datetime
zerotime = datetime.datetime.fromtimestamp(0)

from Zope.ComponentArchitecture import getAdapter
from Zope.App.DublinCore.IZopeDublinCore import IZopeDublinCore
from Zope.App.OFS.Container.Views.VFS.VFSContainerView import \
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
        'See Zope.Publisher.VFS.IVFSDirectoryPublisher.IVFSDirectoryPublisher'
        if self.context.hasServiceManager() and name == '++etc++Services':
            return True
        return super(FolderView, self).exists(name)


    def listdir(self, with_stats=0, pattern='*'):
        'See Zope.Publisher.VFS.IVFSDirectoryPublisher.IVFSDirectoryPublisher' 
        result = super(FolderView, self).listdir(with_stats, pattern)
        if self.context.hasServiceManager():
            result = [('++etc++Services', self._getServiceManagerStat())] \
                     + result
        return result
