##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Base class for DAV functional tests.

$Id: dav.py,v 1.2 2003/09/21 17:30:44 jim Exp $
"""

from zope.testing.functional import HTTPTestCase
from zope.app.content.zpt import ZPTPage
from zope.app.content.folder import Folder
from transaction import get_transaction

__metaclass__ = type

class DAVTestCase(HTTPTestCase):

    def createFolders(self, path):
        """createFolders('/a/b/c/d') would traverse and/or create three nested
        folders (a, b, c) and return a tuple (c, 'd') where c is a Folder
        instance at /a/b/c."""
        folder = self.getRootFolder()
        if path[0] == '/':
            path = path[1:]
        path = path.split('/')
        for id in path[:-1]:
            try:
                folder = folder[id]
            except KeyError:
                folder[id] = Folder()
                folder = folder[id]
        return folder, path[-1]

    def createObject(self, path, obj):
        folder, id = self.createFolders(path)
        folder[id] = obj
        get_transaction().commit()

    def addPage(self, path, content):
        page = ZPTPage()
        page.source = content
        self.createObject(path, page)

