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
"""VFS-View for IContainer

VFS-view implementation for a generic container. It should really work for
all container-like objects. There is not much that can be done differently.

$Id: VFSContainerView.py,v 1.4 2002/12/20 09:25:37 srichter Exp $
"""
import fnmatch
import datetime
zerotime = datetime.datetime.fromtimestamp(0)

from Zope.ComponentArchitecture import \
     getView, queryView, getAdapter, queryAdapter, createObject

from Zope.Proxy.ProxyIntrospection import removeAllProxies

from Zope.Publisher.Exceptions import NotFound
from Zope.Publisher.VFS.VFSView import VFSView
from Zope.Publisher.VFS.IVFSPublisher import IVFSPublisher
from Zope.Publisher.VFS.VFSRequest import VFSRequest
from Zope.Publisher.VFS.IVFSDirectoryPublisher import IVFSDirectoryPublisher

from Zope.App.OFS.Container.IContainer import IContainer
from Zope.App.DublinCore.IZopeDublinCore import IZopeDublinCore


class VFSContainerView(VFSView):

    __implements__ =  IVFSDirectoryPublisher, VFSView.__implements__

    # This attribute specifies which type of container (factory id) should be
    # used when a directory is created.
    _directory_type = 'Container'

    ############################################################
    # Implementation methods for interface
    # Zope.Publisher.VFS.IVFSDirectoryPublisher

    def exists(self, name):
        'See Zope.Publisher.VFS.IVFSDirectoryPublisher.IVFSDirectoryPublisher'
        try:
            self.publishTraverse(self.request, name)
        except NotFound:
            return 0
        return 1

    def listdir(self, with_stats=0, pattern='*'):
        'See Zope.Publisher.VFS.IVFSDirectoryPublisher.IVFSDirectoryPublisher'
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
                view = queryView(obj, 'vfs', self.request)
                if view is not None:
                    stat = view.stat()
                else:
                    # Even though this object has no VFS view, we should
                    # display it.
                    stat = (16384+511, 0, 0, 0, "nouser", "nogroup", 0,
                            zerotime, zerotime, zerotime)
                result.append((file, stat))
                
        return result
    

    def mkdir(self, name, mode=777):
        'See Zope.Publisher.VFS.IVFSDirectoryPublisher.IVFSDirectoryPublisher'
        if not (name in self.context):
            adding = getView(self.context, "+", self.request)
            adding.setContentName(name)
            add = queryView(adding, self._directory_type, self.request)
            add()

    def remove(self, name):
        'See Zope.Publisher.VFS.IVFSDirectoryPublisher.IVFSDirectoryPublisher'
        container = removeAllProxies(self.context)
        container.__delitem__(name)
        # XXX: We should have a ObjectRemovedEvent here

    def rmdir(self, name):
        'See Zope.Publisher.VFS.IVFSDirectoryPublisher.IVFSDirectoryPublisher'
        self.remove(name)

    def rename(self, old, new):
        'See Zope.Publisher.VFS.IVFSDirectoryPublisher.IVFSDirectoryPublisher'
        container = self.context
        content = container[old]
        self.remove(old)
        # Re-add the object
        adding = getView(container, "+", self.request)
        adding.setContentName(new)
        content = adding.add(content)

    def writefile(self, name, mode, instream, start=0):
        'See Zope.Publisher.VFS.IVFSDirectoryPublisher.IVFSDirectoryPublisher'
        # Find the extension
        ext_start = name.rfind('.')
        if ext_start > 0:
            ext = name[ext_start:]
        else:
            ext = "."

        # Create and add a new content object.
        adding = getView(self.context, "+", self.request)
        adding.setContentName(name)
        add = queryView(adding, ext, self.request)
        if add is None:
            # We do not know about this content type, so choose the generic
            # one.
            add = queryView(adding, ".", self.request)

        add(mode, instream, start)
                    
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
        dc = getAdapter(self.context, IZopeDublinCore)
        if dc is not None:
            created = dc.created
            modified = dc.modified
        else:
            created = zerotime
            modified = zerotime

        # It happens that modified might still be None, so make sure we return
        # a date. *nix then uses the created date as the modified one, which we
        # do too. ;)
        if modified is None:
            modified = created

        dir_mode = 16384 + 504
        uid = "nouser"
        gid = "nogroup"
        return (dir_mode, 0, 0, 0, uid, gid, 4096, modified, modified,
                created)


    ######################################
    # from: Zope.Publisher.VFS.IVFSPublisher.IVFSPublisher

    def publishTraverse(self, request, name):
        'See Zope.Publisher.VFS.IVFSPublisher.IVFSPublisher'
        # This is a nice way of doing the name lookup; this way we can keep
        # all the extension handeling code in the Traverser code.
        traverser = getView(self.context, '_traverse', request)
        return traverser.publishTraverse(request, name)

    #
    ############################################################


