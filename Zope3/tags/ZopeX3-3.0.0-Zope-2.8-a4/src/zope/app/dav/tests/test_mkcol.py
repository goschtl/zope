##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""MKCOL tests

$Id$
"""
from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.tests import ztapi
from zope.app.traversing.api import traverse
from zope.app.site.tests.placefulsetup import PlacefulSetup

from zope.app.container.interfaces import IWriteContainer
from zope.app.filerepresentation.interfaces import IWriteDirectory
from zope.app.container.directory import noop

from zope.app.folder.interfaces import IFolder
from zope.app.filerepresentation.interfaces import IDirectoryFactory
from zope.app.container.directory import Cloner

from zope.app.http.put import NullResource
from zope.app.dav import mkcol
from zope.app.dav.tests.test_propfind import _createRequest, File

class TestPlacefulMKCOL(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        PlacefulSetup.buildFolders(self)
        ztapi.provideAdapter(IWriteContainer, IWriteDirectory, noop)
        ztapi.provideAdapter(IFolder, IDirectoryFactory, Cloner)

    def test_mkcol_not_folderish(self):
        root = self.rootFolder
        request = _createRequest('')
        container = traverse(root, 'folder1')
        file = File('bla', 'text/plain', 'bla', container)
        container['bla'] = file
        file = traverse(container, 'bla')
        nr = NullResource(file, 'mkcol_test')
        mkcol.NullResource(nr, request).MKCOL()
        self.assertEqual(request.response.getStatus(), 403)

    def test_mkcol_not_existing(self):
        root = self.rootFolder
        request = _createRequest('')
        container = traverse(root, 'folder1')
        self.failIf('mkcol_test' in container.keys())
        nr = NullResource(container, 'mkcol_test')
        mkcol.NullResource(nr, request).MKCOL()
        self.assertEqual(request.response.getStatus(), 201)
        self.failIf('mkcol_test' not in container.keys())

    def test_mkcol_existing(self):
        root = self.rootFolder
        request = _createRequest('')
        container = traverse(root, 'folder1')
        self.failIf('mkcol_test' in container.keys())
        nr = NullResource(container, 'folder1_1')
        mkcol.MKCOL(nr, request).MKCOL()
        self.assertEqual(request.response.getStatus(), 405)

    def test_mkcol_non_empty_body(self):
        root = self.rootFolder
        request = _createRequest('bla')
        container = traverse(root, 'folder1')
        self.failIf('mkcol_test' in container.keys())
        nr = NullResource(container, 'mkcol_test')
        mkcol.NullResource(nr, request).MKCOL()
        self.failIf('mkcol_test' in container.keys())
        self.assertEqual(request.response.getStatus(), 415)

def test_suite():
    return TestSuite((
        makeSuite(TestPlacefulMKCOL),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
