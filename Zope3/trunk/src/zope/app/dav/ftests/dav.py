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

$Id: dav.py,v 1.5 2004/03/13 23:00:48 srichter Exp $
"""
from persistent import Persistent
from transaction import get_transaction
from zope.interface import implements
from zope.testing.functional import HTTPTestCase

from zope.app.folder import Folder
from zope.app.annotation.interfaces import IAttributeAnnotatable

class Page(Persistent):
    implements(IAttributeAnnotatable)    

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
        page = Page()
        page.source = content
        self.createObject(path, page)
