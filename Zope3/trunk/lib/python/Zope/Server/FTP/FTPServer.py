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

$Id: FTPServer.py,v 1.2 2002/06/10 23:29:35 jim Exp $
"""
import asyncore
from FTPServerChannel import FTPServerChannel
from Zope.Server.ServerBase import ServerBase
from Zope.Server.VFS.IFilesystemAccess import IFilesystemAccess



class FTPServer(ServerBase):
    """Generic FTP Server"""

    channel_class = FTPServerChannel
    SERVER_IDENT = 'Zope.Server.FTPServer'


    def __init__(self, ip, port, fs_access, *args, **kw):

        assert IFilesystemAccess.isImplementedBy(fs_access)
        self.fs_access = fs_access

        super(FTPServer, self).__init__(ip, port, *args, **kw)


if __name__ == '__main__':
    from Zope.Server.TaskThreads import ThreadedTaskDispatcher
    from Zope.Server.VFS.OSFileSystem import OSFileSystem
    from Zope.Server.VFS.TestFilesystemAccess import TestFilesystemAccess
    td = ThreadedTaskDispatcher()
    td.setThreadCount(4)
    fs = OSFileSystem('/')
    fs_access = TestFilesystemAccess(fs)
    FTPServer('', 8021, fs_access, task_dispatcher=td)
    try:
        while 1:
            asyncore.poll(5)
            print 'active channels:', FTPServerChannel.active_channels
    except KeyboardInterrupt:
        print 'shutting down...'
        td.shutdown()
