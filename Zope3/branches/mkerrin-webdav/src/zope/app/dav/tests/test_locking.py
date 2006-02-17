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
"""Test Locking

$Id$
"""
from cStringIO import StringIO
from xml.dom import minidom
from unittest import TestCase, TestSuite, main, makeSuite

import transaction
from ZODB.tests.util import DB

from zope.publisher.browser import TestRequest
from zope.app.component.testing import PlacefulSetup
from zope.app.traversing.api import traverse

from zope.interface import Interface
from zope.pagetemplate.tests.util import normalize_xml
from zope.schema.interfaces import IText, ITextLine, IDatetime, ISequence, IInt
from zope.app import zapi
from zope.app.testing import ztapi
from zope.app.locking.interfaces import ILockable, ILockTracker
from zope.app.locking.adapter import LockingAdapterFactory, LockingPathAdapter
from zope.app.locking.storage import ILockStorage, PersistentLockStorage
from zope.app.traversing.interfaces import IPathAdapter
from zope.app.keyreference.interfaces import IKeyReference
from zope.security.management import newInteraction, endInteraction
from zope.security.testing import Principal, Participation

from zope.app.dav.locking import LOCK
from zope.app.dav import interfaces
from zope.app.dav import widget
from zope.app.dav.fields import IDAVXMLSubProperty, IDAVOpaqueField
from zope.app.dav.adapter import DAVSchemaAdapter, ActiveLock

from unitfixtures import File, Folder, FooZPT

# copied from zope.app.locking.tests
class FakeKeyReference(object):
    """Fake keyref for testing"""
    def __init__(self, object):
        self.object = object

    def __call__(self):
        return self.object

    def __hash__(self):
        return id(self.object)

    def __cmp__(self, other):
        return cmp(id(self.object), id(other.object))


def _createRequest(data, headers = None, skip_headers = None):
    if headers is None:
        headers = {'Content-type': 'text/xml',
                   'Depth': '0'}

    body = '''<?xml version="1.0" encoding="utf-8"?>
    <lockinfo xmlns="DAV:">
      <locktype><%s/></locktype>
      <lockscope><%s/></lockscope>
      <owner>%s</owner>
    </lockinfo>
    ''' %(data['locktype'], data['lockscope'], data['owner'])

    _environ = {'CONTENT_TYPE': 'text/xml',
                'CONTENT_LENGTH': str(len(body))}

    if headers is not None:
        for key, value in headers.items():
            _environ[key.upper().replace('-', '_')] = value

    if skip_headers is not None:
        for key in skip_headers:
            if _environ.has_key(key.upper()):
                del _environ[key.upper()]

    request = TestRequest(StringIO(body), _environ)

    return request


class TestPlacefulLOCK(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        PlacefulSetup.buildFolders(self)

        root = self.rootFolder
        zpt = FooZPT()
        self.content = "some content\n for testing"
        file = File('spam', 'text/plain', self.content)
        folder = Folder('bla')
        root['file'] = file
        root['zpt'] = zpt
        root['folder'] = folder
        self.zpt = traverse(root, 'zpt')
        self.file = traverse(root, 'file')
        self.folder = traverse(root, 'folder')

        ztapi.provideAdapter(Interface, IKeyReference, FakeKeyReference)
        ztapi.provideAdapter(Interface, ILockable, LockingAdapterFactory)
        ztapi.provideAdapter(None, IPathAdapter, LockingPathAdapter,
                             "locking")
        storage = PersistentLockStorage()
        ztapi.provideUtility(ILockStorage, storage)
        ztapi.provideUtility(ILockTracker, storage)

        ztapi.provideAdapter(Interface, interfaces.IActiveLock,
                             ActiveLock)
        ztapi.provideAdapter(Interface, interfaces.IDAVLockSchema,
                             DAVSchemaAdapter)

        ztapi.browserViewProviding(IText, widget.TextDAVWidget,
                                   interfaces.IDAVWidget)
        ztapi.browserViewProviding(IInt, widget.TextDAVWidget,
                                   interfaces.IDAVWidget)
        ztapi.browserViewProviding(ITextLine, widget.TextDAVWidget,
                                   interfaces.IDAVWidget)
        ztapi.browserViewProviding(IDatetime, widget.DatetimeDAVWidget,
                                   interfaces.IDAVWidget)
        ztapi.browserViewProviding(ISequence, widget.SequenceDAVWidget,
                                   interfaces.IDAVWidget)
        ztapi.browserViewProviding(interfaces.IXMLEmptyElementList,
                                   widget.XMLEmptyElementListDAVWidget,
                                   interfaces.IDAVWidget)
        ztapi.browserViewProviding(interfaces.IDAVXMLSubProperty,
                                   widget.DAVXMLSubPropertyWidget,
                                   interfaces.IDAVWidget)
        ztapi.browserViewProviding(IDAVOpaqueField,
                                   widget.DAVOpaqueWidget,
                                   interfaces.IDAVWidget)

        self.db = DB()
        self.conn = self.db.open()
        root = self.conn.root()
        root['Application'] = self.rootFolder
        transaction.commit()

    def tearDown(self):
        PlacefulSetup.tearDown(self)
        self.db.close()

    def _simpleLock(self, object, username = 'michael', headers = None):
        michael = Principal(username)
        mparticipation = Participation(michael)
        endInteraction()
        newInteraction(mparticipation)
        request = _createRequest(
            data = {'lockscope': 'exclusive',
                    'locktype': 'write',
                    'owner': '<href>mailto:michael@linux</href>'},
            headers = headers)
        lock = LOCK(object, request)
        lock.LOCK()
        endInteraction()
        return request.response

    def test_non_webdav_but_locked_file(self):
        michael = Principal('michael')
        mparticipation = Participation(michael)
        endInteraction()
        newInteraction(mparticipation)
        file = self.file
        lockable = ILockable(file)
        lock = lockable.lock()
        lockinfo = lockable.getLockInfo()
        endInteraction()

        self._simpleLock(self.file, 'michael')

    def test_file_is_locked(self):
        self._simpleLock(self.file, 'michael')
        file = self.file

        lockable = ILockable(file)
        self.assertEqual(lockable.locked(), True)
        lockinfo = lockable.getLockInfo()
        self.assert_(lockinfo.target is file)
        lockscope = lockinfo['lockscope']
        self.assert_(len(lockscope) == 1)
        self.assert_(lockscope[0] == u'exclusive')
        locktype = lockinfo['locktype']
        self.assert_(len(locktype) == 1)
        self.assert_(locktype[0] == u'write')

    def test_alreadylocked(self):
        self._simpleLock(self.file, 'michael')
        file = self.file
        lockable = ILockable(file)
        self.assertEqual(lockable.locked(), True)

        response = self._simpleLock(self.file, 'michael')
        self.assertEqual(response.getStatus(), 423)

    def test_depthinf(self):
        response = self._simpleLock(self.folder, 'michael',
                                    {'DEPTH': 'infinity'})
        self.assertEqual(response.getStatus(), 200)
        # assert that the depth infinity locked any subobjects
        locktracker = zapi.getUtility(ILockTracker)
        self.assert_(locktracker.getAllLocks() > 1)

    def test_depthinf_conflict(self):
        file1 = self.folder.items()[0][1]
        response = self._simpleLock(file1, 'michael')
        self.assertEqual(response.getStatus(), 200)
        response = self._simpleLock(self.folder, 'michael',
                                    {'DEPTH': 'infinity'})
        self.assertEqual(response.getStatus(), 207)

        expected = '''<?xml version="1.0" encoding="utf-8"?>
        <multistatus xmlns="DAV:">
          <response>
            <href>http://127.0.0.1/folder/1</href>
            <propstat>
              <prop><lockdiscovery/></prop>
              <status>HTTP/1.1 423 Locked</status>
            </propstat>
          </response>
        </multistatus>'''

        s1 = normalize_xml(response.consumeBody())
        s2 = normalize_xml(expected)
        self.assertEqual(s1, s2)
        

def test_suite():
    return TestSuite((
        makeSuite(TestPlacefulLOCK),
        ))

if __name__ == '__main__':
    main(defaultTest = 'test_suite')
