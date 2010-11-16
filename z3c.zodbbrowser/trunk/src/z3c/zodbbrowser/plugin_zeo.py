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
"""Plugin for ZODB ZEO storage."""

import transaction
from ZODB import DB
import ZEO.ClientStorage

from wax import *
from z3c.zodbbrowser.bases import BaseSourcePlugin


class OpenClientStorage(Dialog):
    """An "open" dialog for ClientStorages."""

    def Body(self):
        label = Label(self, 'IP address')
        self.AddComponent(label, expand='h', border=7)
        self.ip = TextBox(self, size=(100,25))
        self.ip.SetValue('127.0.0.1')
        self.AddComponent(self.ip, expand='h', border=5)

        label = Label(self, 'Port')
        self.AddComponent(label, expand='h', border=7)
        self.port = TextBox(self, size=(100,25))
        self.port.SetValue('9000')
        self.AddComponent(self.port, expand='h', border=5)


class ClientStoragePlugin(BaseSourcePlugin):

    storage = None
    db = None
    connection = None
    root = None

    ip = None
    port = None

    def open_direct(self, address, port):
        """Open ZODB.

        Returns a tuple consisting of: (root, connection, db, storage)

        The same tuple must be passed to close_zodb() in order to close the DB.

        """
        self.storage = ZEO.ClientStorage.ClientStorage(
            (address, port), read_only=True)
        self.db = DB(self.storage)
        self.connection = self.db.open()
        self.root = self.connection.root()
        return True

    def open(self, parent):
        dlg = OpenClientStorage(parent, "Open ClientStorage")
        try:
            result = dlg.ShowModal()
            if result == 'ok':
                self.ip = dlg.ip.GetValue().encode('ascii')
                self.port = int(dlg.port.GetValue())
                return self.open_direct(self.ip, self.port)
        finally:
            dlg.Destroy()
        return False

    def close(self):
        """Closes the ZODB.

        This function MUST be called at the end of each program !!!
        """
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
        return "ClientStorage at %s:%s" % (self.ip, self.port)


def register(registry):
    registry['source'].extend([
        ('ClientStorage', 'cs', ClientStoragePlugin)])
