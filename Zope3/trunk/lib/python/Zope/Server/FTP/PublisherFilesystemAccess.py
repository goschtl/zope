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
"""Implementation of IFilesystemAccess intended only for testing.

$Id: PublisherFilesystemAccess.py,v 1.3 2002/06/20 15:55:09 jim Exp $
"""

from cStringIO import StringIO
from Zope.Exceptions import Unauthorized
from Zope.App.Security.Registries.PrincipalRegistry import principalRegistry

from Zope.Server.VFS.PublisherFileSystem import PublisherFileSystem
from Zope.Server.VFS.IFilesystemAccess import IFilesystemAccess
from Zope.Server.VFS.IUsernamePassword import IUsernamePassword


class PublisherFilesystemAccess:

    __implements__ = IFilesystemAccess

    def __init__(self, request_factory):
        self.request_factory = request_factory


    def authenticate(self, credentials):
        assert IUsernamePassword.isImplementedBy(credentials)
        env = {'credentials' : credentials}
        request = self.request_factory(StringIO(''), StringIO(), env)
        id = principalRegistry.authenticate(request)
        if id is None:
            raise Unauthorized


    def open(self, credentials):
        return PublisherFileSystem(credentials, self.request_factory)


