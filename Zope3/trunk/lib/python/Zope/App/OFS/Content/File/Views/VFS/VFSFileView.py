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

$Id: VFSFileView.py,v 1.3 2002/06/29 15:41:37 srichter Exp $
"""

import time
from Zope.Publisher.VFS.VFSView import VFSView
from Zope.Publisher.VFS.IVFSFilePublisher import IVFSFilePublisher


class VFSFileView(VFSView):

    __implements__ = IVFSFilePublisher, VFSView.__implements__


    ############################################################
    # Implementation methods for interface
    # Zope.Publisher.VFS.IVFSFilePublisher.

    def read(self, mode, outstream, start = 0, end = -1):
        """See Zope.Publisher.VFS.IVFSFilePublisher.IVFSFilePublisher"""
        data = self.context.getData()
        try:
            if start != 0: data = data[start:]
            if end != -1: data = data[:end]
        except TypeError:
            pass
        outstream.write(data)


    def write(self, mode, instream, start = 0):
        """See Zope.Publisher.VFS.IVFSFilePublisher.IVFSFilePublisher"""
        try:
            instream.seek(start)
        except:
            pass
        self.context.setData(instream.read())


    def check_writable(self, mode):
        """See Zope.Publisher.VFS.IVFSFilePublisher.IVFSFilePublisher"""
        return 1

    ######################################
    # from: Zope.Publisher.VFS.IVFSObjectPublisher.IVFSObjectPublisher

    def isdir(self):
        """See Zope.Publisher.VFS.IVFSObjectPublisher.IVFSObjectPublisher"""
        return 0


    def isfile(self):
        """See Zope.Publisher.VFS.IVFSObjectPublisher.IVFSObjectPublisher"""
        return 1


    def stat(self):
        """See Zope.Publisher.VFS.IVFSObjectPublisher.IVFSObjectPublisher"""
        t = time.time()
        size = 0
        if hasattr(self.context, 'getSize'):
            size = self.context.getSize()
        uid = 0
        gid = 0
        return (511, 0, 0, 0, uid, gid, size, t, t, t)


    ######################################
    # from: Zope.Publisher.VFS.IVFSPublisher.IVFSPublisher

    def publishTraverse(self, request, name):
        """See Zope.Publisher.VFS.IVFSPublisher.IVFSPublisher"""
        return getattr(self, name)

    #
    ############################################################
