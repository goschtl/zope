##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
import logging

from zope.app.appsetup.interfaces import IApplicationFactory
from zope.app.appsetup.interfaces import DatabaseOpened
from zope.event import notify
from zope.app.zodb import ROOT_NAME, VERSION_COOKIE
from zope.interface import implements
from zope.app.applicationcontrol.applicationcontrol \
     import applicationControllerRoot
from zope.app.publication.zopepublication import Cleanup

class ZODBApplicationFactory:

    implements(IApplicationFactory)

    def __init__(self, db):
        self.db = db

    def prepare(self):
        notify(DatabaseOpened(self.db))

    def openedConnection(self, conn):
        # Hook for auto-refresh
        pass

    def __call__(self, request):
        # If the first name is '++etc++process', then we should
        # get it rather than look in the database!
        stack = request.getTraversalStack()

        if '++etc++process' in stack:
            return applicationControllerRoot

        # Open the database.
        version = request.get(VERSION_COOKIE, '')
        conn = self.db.open(version)

        cleanup = Cleanup(conn.close)
        request.hold(cleanup)  # Close the connection on request.close()

        self.openedConnection(conn)
        #conn.setDebugInfo(getattr(request, 'environ', None), request.other)

        root = conn.root()
        app = root.get(ROOT_NAME, None)

        return app
