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
"""

$Id: VFSContainerView.py,v 1.3 2002/06/29 15:41:37 srichter Exp $
"""
import fnmatch
import time

from Zope.ComponentArchitecture import getView
from Zope.Publisher.VFS.VFSView import VFSView
from Zope.Publisher.VFS.IVFSPublisher import IVFSPublisher
from Zope.Publisher.VFS.VFSRequest import VFSRequest

from Zope.Publisher.VFS.IVFSDirectoryPublisher import IVFSDirectoryPublisher
from Zope.App.OFS.Container.IContainer import IContainer 

# XXX hard coded object types.
from Zope.App.OFS.Content.File.File import File
from Zope.App.OFS.Content.Folder.Folder import Folder


class VFSContainerView(VFSView):

    __implements__ =  IVFSDirectoryPublisher, VFSView.__implements__


    ############################################################
    # Implementation methods for interface
    # Zope.Publisher.VFS.IVFSDirectoryPublisher

    def exists(self, name):
        'See Zope.Publisher.VFS.IVFSDirectoryPublisher.IVFSDirectoryPublisher'
        return name in self.context
    

    def listdir(self, with_stats=0, pattern='*'):
        'See Zope.Publisher.VFS.IVFSDirectoryPublisher.IVFSDirectoryPublisher'
        t = time.time()
        file_list = self.context.keys()
        # filter them using the pattern
        file_list = list(
            filter(lambda f, p=pattern, fnm=fnmatch.fnmatch: fnm(f, p),
                   file_list))
        # sort them alphabetically
        file_list.sort()
        if not with_stats:
            result = file_list
        else:
            result = []
            for file in file_list:
                obj = self.context[file]
                size = 0
                # XXX Should be much nicer
                if IContainer.isImplementedBy(obj):
                    dir_mode = 16384 + 511
                else:
                    dir_mode = 511
                if hasattr(obj, 'getSize'):
                    size = obj.getSize()
                stat = (dir_mode, 0, 0, 0, 0, 0, size, t, t, t)
                if stat is not None:
                    result.append((file, stat))
        return result
    

    def mkdir(self, name, mode=777):
        'See Zope.Publisher.VFS.IVFSDirectoryPublisher.IVFSDirectoryPublisher'
        if not (name in self.context):
            obj = Folder()
            self.context.setObject(name, obj)

    def remove(self, name):
        'See Zope.Publisher.VFS.IVFSDirectoryPublisher.IVFSDirectoryPublisher'
        del self.context[name]

    def rmdir(self, name):
        'See Zope.Publisher.VFS.IVFSDirectoryPublisher.IVFSDirectoryPublisher'
        del self.context[name]

    def rename(self, old, new):
        'See Zope.Publisher.VFS.IVFSDirectoryPublisher.IVFSDirectoryPublisher'
        obj = self.context[old]
        del self.context[old]
        self.context.setObject(new, obj)        


    def writefile(self, name, mode, instream, start=0):
        'See Zope.Publisher.VFS.IVFSDirectoryPublisher.IVFSDirectoryPublisher'
        # XXX This should become much, much smarter later. Based on the
        # data and the file ending, it should pick the right object type. 
        # *** Waiting for Jim's file extension proposal and code to land ***
        if not (name in self.context):
            obj = File()
            self.context.setObject(name, obj)
        else:
            obj = self.context[name]

        vfs_view = getView(obj, 'vfs', self.request)
        vfs_view.write(mode, instream, start)

    def check_writable(self, name):
        'See Zope.Publisher.VFS.IVFSDirectoryPublisher.IVFSDirectoryPublisher'
        # XXX Cheesy band aid :-)
        return 1


    ######################################
    # from: Zope.Publisher.VFS.IVFSObjectPublisher.IVFSObjectPublisher

    def isdir(self):
        'See Zope.Publisher.VFS.IVFSObjectPublisher.IVFSObjectPublisher'
        return 1

    def isfile(self):
        'See Zope.Publisher.VFS.IVFSObjectPublisher.IVFSObjectPublisher'
        return 0

    def stat(self):
        'See Zope.Publisher.VFS.IVFSObjectPublisher.IVFSObjectPublisher'
        dir_mode = 16384
        t = time.time()
        uid = 0
        gid = 0
        return (dir_mode+512, 0, 0, 0, uid, gid, 4096, t, t, t)


    ######################################
    # from: Zope.Publisher.VFS.IVFSPublisher.IVFSPublisher

    def publishTraverse(self, request, name):
        'See Zope.Publisher.VFS.IVFSPublisher.IVFSPublisher'
        return getattr(self, name)

    #
    ############################################################
