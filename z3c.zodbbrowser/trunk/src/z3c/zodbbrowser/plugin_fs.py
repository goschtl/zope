# -*- coding: UTF-8 -*-
##############################################################################
#
# Copyright (c) 2004-2006 Zope Foundation and Contributors.
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
"""Plugin for ZODB FileStorage data source."""

import transaction
from ZODB import FileStorage, DB

from wax import *
from z3c.zodbbrowser.bases import BaseSourcePlugin


class ZODBFSPlugin(BaseSourcePlugin):

    storage = None
    db = None
    connection = None
    root = None
    filename = ""

    def open_direct(self, Path):
        """Open ZODB.

        Returns a tuple consisting of: (root, connection, db, storage).

        The same tuple must be passed to close_zodb() in order to close the DB.

        """
        self.storage = FileStorage.FileStorage(Path, read_only=True)
        self.db = DB(self.storage)
        self.connection = self.db.open()
        self.root = self.connection.root()
        return True

    def open(self, parent):
        dlg = FileDialog(parent, open=1)
        try:
            result = dlg.ShowModal()
            if result == 'ok':
                self.filename = dlg.GetPaths()[0]
                return self.open_direct(self.filename)
        finally:
            dlg.Destroy()

        return False

    def close(self):
        """Closes the ZODB.

        This function MUST be called at the end of each program !!!
        """
        # XXX This is a bad place for this function:
        # a) the code is duplicated in each source plugin
        # b) if it MUST be called, we better make sure it is.
        transaction.abort()
        self.connection.close()
        self.db.close()
        self.storage.close()
        self.filename = ""
        return True

    def getSupportedDisplays(self):
        return ['tree']

    def getDataForDisplay(self, mode):
        return self.root

    def getTitle(self):
        return self.filename


def register(registry):
    registry['source'].extend([
        ('FileStorage', 'fs', ZODBFSPlugin)])
