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
Revision information:

$Id: test_rename.py,v 1.4 2004/02/24 16:51:25 philikon Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.traversing import traverse
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.component import getAdapter
from zope.app.tests import ztapi
from zope.app.interfaces.copypastemove import IObjectMover
from zope.app.interfaces.container import IContainer
from zope.app.copypastemove import ObjectMover
from zope.exceptions import NotFoundError, DuplicationError
from zope.app.copypastemove import rename

class File:
    pass

class RenameTest(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        PlacefulSetup.buildFolders(self)
        ztapi.provideAdapter(None, IObjectMover, ObjectMover)

    def test_simplerename(self):
        root = self.rootFolder
        folder1 = traverse(root, 'folder1')
        self.failIf('file1' in folder1)
        folder1['file1'] = File()
        rename(folder1, 'file1', 'my_file1')
        self.failIf('file1' in folder1)
        self.failUnless('my_file1' in folder1)

    def test_renamenonexisting(self):
        root = self.rootFolder
        folder1 = traverse(root, 'folder1')
        self.failIf('a_test_file' in folder1)
        self.assertRaises(NotFoundError, rename, folder1, 'file1', 'my_file1')

    def test_renamesamename(self):
        root = self.rootFolder
        folder1 = traverse(root, 'folder1')
        self.failIf('file1' in folder1)
        self.failIf('file2' in folder1)
        folder1['file1'] = File()
        folder1['file2'] = File()
        self.assertRaises(DuplicationError, rename, folder1, 'file1', 'file2')

def test_suite():
    return TestSuite((
        makeSuite(RenameTest),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
