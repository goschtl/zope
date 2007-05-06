##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
FTP server factories.
"""

from zope.app.twisted.server import ServerType
from zope.app.twisted.ftp.server import FTPFactory

from utils import FTPRequestFactory

def createFTPFactory(db):
    request_factory = FTPRequestFactory(db)

    factory = FTPFactory(request_factory)

    return factory

ftpserver = ServerType(createFTPFactory, 8021)
