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

$Id: ServiceManagerView.py,v 1.1 2002/12/23 08:15:38 srichter Exp $
"""
import datetime
zerotime = datetime.datetime.fromtimestamp(0)

from Zope.Publisher.VFS.VFSView import VFSView
from Zope.Publisher.VFS.IVFSDirectoryPublisher import \
     IVFSDirectoryPublisher

class ServiceManagerView(VFSView):
    """Specific ServiceManager VFS view."""

    __implments__ = IVFSDirectoryPublisher, VFSView.__implements__

    ############################################################
    # Implementation methods for interface
    # Zope.Publisher.VFS.IVFSDirectoryPublisher

    def exists(self, name):
        'See Zope.Publisher.VFS.IVFSDirectoryPublisher.IVFSDirectoryPublisher'
        if name == 'Packages':
            return True
        return False

    def listdir(self, with_stats=0, pattern='*'):
        'See Zope.Publisher.VFS.IVFSDirectoryPublisher.IVFSDirectoryPublisher' 
        return [('Packages', (16384+511, 0, 0, 0, "nouser", "nogroup", 0,
                            zerotime, zerotime, zerotime)) ]
    
    def mkdir(self, name, mode=777):
        'See Zope.Publisher.VFS.IVFSDirectoryPublisher.IVFSDirectoryPublisher'
        pass

    def remove(self, name):
        'See Zope.Publisher.VFS.IVFSDirectoryPublisher.IVFSDirectoryPublisher'
        pass

    def rmdir(self, name):
        'See Zope.Publisher.VFS.IVFSDirectoryPublisher.IVFSDirectoryPublisher'
        pass

    def rename(self, old, new):
        'See Zope.Publisher.VFS.IVFSDirectoryPublisher.IVFSDirectoryPublisher'
        pass

    def writefile(self, name, mode, instream, start=0):
        'See Zope.Publisher.VFS.IVFSDirectoryPublisher.IVFSDirectoryPublisher'
        pass

    def check_writable(self, name):
        'See Zope.Publisher.VFS.IVFSDirectoryPublisher.IVFSDirectoryPublisher'
        return False


    ######################################
    # from: Zope.Publisher.VFS.IVFSObjectPublisher.IVFSObjectPublisher

    def isdir(self):
        'See Zope.Publisher.VFS.IVFSObjectPublisher.IVFSObjectPublisher'
        return True

    def isfile(self):
        'See Zope.Publisher.VFS.IVFSObjectPublisher.IVFSObjectPublisher'
        return False

    def stat(self):
        'See Zope.Publisher.VFS.IVFSObjectPublisher.IVFSObjectPublisher'
        return (16384+511, 0, 0, 0, "nouser", "nogroup", 4096,
                 zerotime, zerotime, zerotime)

    ######################################
    # from: Zope.Publisher.VFS.IVFSPublisher.IVFSPublisher

    def publishTraverse(self, request, name):
        'See Zope.Publisher.VFS.IVFSPublisher.IVFSPublisher'
        return None
    #
    ############################################################
