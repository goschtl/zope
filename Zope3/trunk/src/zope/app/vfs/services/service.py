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
"""VFS-View for IServiceManager

$Id: service.py,v 1.2 2002/12/25 14:13:30 jim Exp $
"""
import datetime
zerotime = datetime.datetime.fromtimestamp(0)

from zope.publisher.vfs import VFSView
from zope.publisher.interfaces.vfs import \
     IVFSDirectoryPublisher

class ServiceManagerView(VFSView):
    """Specific ServiceManager VFS view."""

    __implments__ = IVFSDirectoryPublisher, VFSView.__implements__

    def exists(self, name):
        'See IVFSDirectoryPublisher'
        if name == 'Packages':
            return True
        return False

    def listdir(self, with_stats=0, pattern='*'):
        'See IVFSDirectoryPublisher'
        return [('Packages', (16384+511, 0, 0, 0, "nouser", "nogroup", 0,
                            zerotime, zerotime, zerotime)) ]

    def mkdir(self, name, mode=777):
        'See IVFSDirectoryPublisher'
        pass

    def remove(self, name):
        'See IVFSDirectoryPublisher'
        pass

    def rmdir(self, name):
        'See IVFSDirectoryPublisher'
        pass

    def rename(self, old, new):
        'See IVFSDirectoryPublisher'
        pass

    def writefile(self, name, mode, instream, start=0):
        'See IVFSDirectoryPublisher'
        pass

    def check_writable(self, name):
        'See IVFSDirectoryPublisher'
        return False

    def isdir(self):
        'See IVFSObjectPublisher'
        return True

    def isfile(self):
        'See IVFSObjectPublisher'
        return False

    def stat(self):
        'See IVFSObjectPublisher'
        return (16384+511, 0, 0, 0, "nouser", "nogroup", 4096,
                 zerotime, zerotime, zerotime)

    def publishTraverse(self, request, name):
        'See IVFSPublisher'
        return None
