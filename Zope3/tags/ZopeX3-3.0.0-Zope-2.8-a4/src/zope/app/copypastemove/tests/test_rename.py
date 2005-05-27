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
"""Test renaming of components

$Id$
"""
from unittest import TestCase, TestSuite, main, makeSuite

from zope.testing.doctestunit import DocTestSuite
from zope.app.tests.placelesssetup import setUp, tearDown
from zope.app.tests import ztapi

from zope.exceptions import NotFoundError, DuplicationError
from zope.app.traversing.api import traverse
from zope.app.site.tests.placefulsetup import PlacefulSetup
from zope.app.container.interfaces import IContainer
from zope.app.copypastemove.interfaces import IObjectMover
from zope.app.copypastemove import ObjectMover
from zope.app.copypastemove import rename

class File(object):
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
    suite = makeSuite(RenameTest)
    suite.addTest(
        DocTestSuite('zope.app.copypastemove',
                     setUp=setUp, tearDown=tearDown),
        )
    return suite

if __name__=='__main__':
    main(defaultTest='test_suite')
