##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Test Copying

$Id$
"""
import unittest

from zope.interface import Interface
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.http import IHTTPRequest
from zope.security.testing import Principal, Participation
from zope.security.management import newInteraction, endInteraction, \
     queryInteraction
from zope.app.testing import ztapi
from zope.app.traversing.api import traverse
from zope.app.traversing.interfaces import TraversalError
from zope.app.component.testing import PlacefulSetup

from zope.app.locking.interfaces import ILockable, ILockStorage
from zope.app.locking.storage import PersistentLockStorage
from zope.app.locking.adapter import LockingAdapterFactory
from zope.app.keyreference.interfaces import IKeyReference
from zope.app.copypastemove import ObjectCopier
from zope.app.copypastemove.interfaces import IObjectCopier

from zope.app.dav.copy import COPY
from zope.app.dav.interfaces import IIfHeader
from zope.app.dav.ifhandler import IfParser

from test_locking import FakeKeyReference
from unitfixtures import File, Folder, ConstraintFolder

class TestDAVCopy(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        PlacefulSetup.buildFolders(self)

        ztapi.provideAdapter(Interface, IObjectCopier, ObjectCopier)

        # locking
        ztapi.provideAdapter(Interface, IKeyReference, FakeKeyReference)
        ztapi.provideAdapter(Interface, ILockable, LockingAdapterFactory)

        storage = self.storage = PersistentLockStorage()
        ztapi.provideUtility(ILockStorage, storage)

        ztapi.provideAdapter((Interface, IHTTPRequest), IIfHeader, IfParser)

    def tearDown(self):
        PlacefulSetup.tearDown(self)
        del self.storage

    def test_copy_file(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        content = 'this is some content'
        file = File('bla', 'text/plain', content, container)
        container['bla'] = file
        file = traverse(container, 'bla')

        self.assertRaises(TraversalError, traverse, container, 'copy_bla')

        request = TestRequest('/folder1/bla',
                              environ = {'REQUEST_METHOD': 'COPY',
                                         'DESTINATION': '/folder1/copy_bla'})
        response = request.response
        copier = COPY(file, request)
        copier.COPY()
        # check for 201 status since the new file will be created.
        self.assertEqual(response.getStatus(), 201)
        newfile = traverse(container, 'copy_bla')
        self.assertEqual(newfile.data, content)

    def test_copy_file_overwrite(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        file = File('bla', 'text/plain', 'this is some content', container)
        container['bla'] = file
        file = traverse(container, 'bla')

        copy_file = File('copy_bla', 'text/plain', 'this is the second file',
                         container)
        container['copy_bla'] = copy_file

        request = TestRequest('/folder1/bla',
                              environ = {'REQUEST_METHOD': 'COPY',
                                         'DESTINATION': '/folder1/copy_bla',
                                         'OVERWRITE': 'T'})
        response = request.response
        copier = COPY(file, request)
        copier.COPY()
        # check for 204 status since the no file is created.
        self.assertEqual(response.getStatus(), 204)
        newfile = traverse(container, 'copy_bla')
        self.assertEqual(newfile.data, 'this is some content')

    def test_copy_file_no_overwrite(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        file = File('bla', 'text/plain', 'this is some content', container)
        container['bla'] = file
        file = traverse(container, 'bla')

        copy_file = File('copy_bla', 'text/plain', 'this is the second file',
                         container)
        container['copy_bla'] = copy_file

        request = TestRequest('/folder1/bla',
                              environ = {'REQUEST_METHOD': 'COPY',
                                         'DESTINATION': '/folder1/copy_bla',
                                         'OVERWRITE': 'F'})
        response = request.response
        copier = COPY(file, request)
        copier.COPY()

        # 412 - precondition failed since overwrite is False.
        self.assertEqual(response.getStatus(), 412)
        newfile = traverse(container, 'copy_bla')
        self.assertEqual(newfile.data, 'this is the second file')

    def test_invalid_copy_request(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        content = 'this is some content'
        file = File('bla', 'text/plain', content, container)
        container['bla'] = file
        file = traverse(container, 'bla')

        request = TestRequest('/folder1/bla',
                              environ = {'REQUEST_METHOD': 'COPY',
                                         'DESTINATION': '/blafolder/copy_bla',
                                         'OVERWRITE': 'X'})
        response = request.response
        copier = COPY(file, request)
        copier.COPY()
        # check for 201 status since the new file will be created.
        self.assertEqual(response.getStatus(), 400)

        # now test a missing destination header.
        request = TestRequest('/folder1/bla',
                              environ = {'REQUEST_METHOD': 'COPY',
                                         'OVERWRITE': 'T'})
        response = request.response
        copier = COPY(file, request)
        copier.COPY()
        # check for 201 status since the new file will be created.
        self.assertEqual(response.getStatus(), 400)

    def test_no_destination_parent(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        content = 'this is some content'
        file = File('bla', 'text/plain', content, container)
        container['bla'] = file
        file = traverse(container, 'bla')

        self.assertRaises(TraversalError, traverse, container, 'copy_bla')

        request = TestRequest('/folder1/bla',
                              environ = {'REQUEST_METHOD': 'COPY',
                                         'DESTINATION': '/blafolder/copy_bla'})
        response = request.response
        copier = COPY(file, request)
        copier.COPY()
        # check for 201 status since the new file will be created.
        self.assertEqual(response.getStatus(), 409)

    def test_destination_file_locked(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        file = File('bla', 'text/plain', 'this is some content', container)
        container['bla'] = file
        file = traverse(container, 'bla')

        dest_file = File('copy_bla', 'text/plain', 'this is the second file',
                         container)
        container['copy_bla'] = dest_file
        dest_file = traverse(container, 'copy_bla')

        # now lock dest_file
        mparticipation = Participation(Principal('michael'))
        if queryInteraction():
            endInteraction()
        newInteraction(mparticipation)
        lockable = ILockable(dest_file)
        lockable.lock()
        endInteraction()

        request = TestRequest('/folder1/bla',
                              environ = {'REQUEST_METHOD': 'COPY',
                                         'DESTINATION': '/folder1/copy_bla',
                                         'OVERWRITE': 'T'})
        response = request.response

        copier = COPY(file, request)
        copier.COPY()

        # 423 - locked
        self.assertEqual(response.getStatus(), 423)
        newfile = traverse(container, 'copy_bla')
        self.assertEqual(newfile.data, 'this is the second file')

    def test_not_copyableTo(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        file = File('bla', 'text/plain', 'this is some content', container)
        container['bla'] = file
        file = traverse(container, 'bla')

        # the ConstraintFolder only allows implementations of IFolder to be
        # added to it - so by copying a file into this folder we should get
        # a conflict and hence a 409 response status.
        folder = ConstraintFolder()
        root['nofilefolder'] = folder

        request = TestRequest('/folder1/bla',
                              environ = {'REQUEST_METHOD': 'COPY',
                                         'DESTINATION': '/nofilefolder/bla',
                                         'OVERWRITE': 'T'})
        response = request.response
        copier = COPY(file, request)
        copier.COPY()

        # conflict - a resource can't be created at the destination.
        self.assertEqual(response.getStatus(), 409)

    def test_source_dest_same(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        file = File('bla', 'text/plain', 'this is some content', container)
        container['bla'] = file
        file = traverse(container, 'bla')

        request = TestRequest('/folder1/bla',
                              environ = {'REQUEST_METHOD': 'COPY',
                                         'DESTINATION': '/folder1/bla',
                                         })
        response = request.response
        copier = COPY(file, request)
        copier.COPY()

        # 403 (Forbidden) _ The source and destination URIs are the same.
        self.assertEqual(response.getStatus(), 403)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestDAVCopy),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest = 'test_suite')
