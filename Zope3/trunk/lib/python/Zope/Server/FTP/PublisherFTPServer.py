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

$Id: PublisherFTPServer.py,v 1.2 2002/06/10 23:29:35 jim Exp $
"""
from FTPServer import FTPServer

from Zope.Server.FTP.PublisherFilesystemAccess import PublisherFilesystemAccess

class PublisherFTPServer(FTPServer):
    """Generic FTP Server"""


    def __init__(self, request_factory, name, ip, port, *args, **kw):
        self.request_factory = request_factory
        fs_access = PublisherFilesystemAccess(request_factory)
        super(PublisherFTPServer, self).__init__(ip, port, fs_access,
                                                 *args, **kw)
