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
"""Test Zope's WebDAV locking support.

$Id$
"""
__docformat__ = 'restructuredtext'

from xml.dom import minidom

from unittest import TestSuite, makeSuite, main

from zope.interface import Interface
from zope.app import zapi
from zope.app.testing import setup, ztapi
from zope.app.locking.interfaces import ILockStorage, ILockable
from zope.app.locking.storage import PersistentLockStorage
from zope.app.locking.adapter import LockingAdapterFactory, LockingPathAdapter
from zope.app.traversing.interfaces import IPathAdapter
from zope.app.file.file import File

from zope.app.security.adapter import LocatingTrustedAdapterFactory

from dav import DAVTestCase

def makeLockBody(data):
    body = '''<?xml version="1.0" encoding="utf-8"?>
    <lockinfo xmlns="DAV:">
    <locktype><%s/></locktype>
    <lockscope><%s/></lockscope>
    <owner>%s</owner>
    </lockinfo>
    ''' %(data['locktype'], data['lockscope'], data['owner'])
    return body


class TestAllowBefore(DAVTestCase):
    # Test for the LOCK and UNLOCK in the Allow header. I use both a OPTIONS
    # request and a 'FROGS' (undefined) request to test for this. The reason
    # for two tests is that I ran into problems getting this to work with the
    # OPTIONS request, has the LOCK, UNLOCK methods are only available when
    # a ILockStorage utility is present.

    def _checkAllowed(self, allowed, expected):
        allowed = [allow.strip() for allow in allowed.split(',')]
        if expected:
            for m in ('LOCK', 'UNLOCK'):
                self.assert_(m in allowed,
                   "%s is NOT in %s" %(m, ', '.join(allowed)))
        else:
            for m in ('LOCK', 'UNLOCK'):
                self.assert_(m not in allowed,
                             "%s is in %s" %(m, ', '.join(allowed)))

    def test_allow_publish(self):
        self._test_allow_publish(False)

    def _test_allow_publish(self, expected):
        result = self.publish('/', env = {'REQUEST_METHOD': 'FROGS'},
                              basic='mgr:mgrpw',
                              handle_errors = True)
        allowed = result.getHeader('Allow')
        self._checkAllowed(allowed, expected)

    def test_allow_options(self):
        self._test_allow_options(False)

    def _test_allow_options(self, expected):
        result = self.publish('/', env = {'REQUEST_METHOD': 'OPTIONS'},
                              basic='mgr:mgrpw')
        allowed = result.getHeader('Allow')
        self._checkAllowed(allowed, expected)

    def test_lock_file_simple(self):
        file = File('some content', 'text/plain')
        self.getRootFolder()['file'] = file
        self.commit()

        body = makeLockBody(
            {'locktype': 'write',
             'lockscope': 'exclusive',
             'owner': '<href>mailto:michael@linux</href>'})
        basic='mgr:mgrpw'
        result = self.publish('/file', basic,
                              env = {'REQUEST_METHOD': 'LOCK',
                                     'CONTENT-LENGTH': len(body)},
                              request_body = body, handle_errors = True)
        respbody = result.getBody()
        self.assertEqual(result.getStatus(), 405)
        allowed = result.getHeader('Allow')
        self._checkAllowed(allowed, False)


class TestAllowAfter(TestAllowBefore):
    pass


class TestLOCK(TestAllowBefore):

    def setUp(self):
        super(TestLOCK, self).setUp()
        sm = zapi.getSiteManager(self.getRootFolder())

        self.storage = storage = PersistentLockStorage()
        setup.addUtility(sm, '', ILockStorage, storage)

        ## create a trusted adapter.
        ztapi.provideAdapter(Interface, ILockable,
                           LocatingTrustedAdapterFactory(LockingAdapterFactory))
##         ztapi.provideAdapter(None, IPathAdapter, LockingPathAdapter,
##                              "locking")
        self.commit()

    def tearDown(self):
        super(TestLOCK, self).tearDown()
        del self.storage

    def test_allow_options(self):
        self._test_allow_options(True)

    def test_allow_publish(self):
        ## XXX - the LOCK, and UNLOCK methods should show up in the allow header
        ## for this test but I can't get this work.
        self._test_allow_publish(True)

    def test_lock_file_simple(self):
        file = File('some content', 'text/plain')
        self.getRootFolder()['file'] = file
        self.commit()

        body = makeLockBody(
            {'locktype': 'write',
             'lockscope': 'exclusive',
             'owner': '<href>mailto:michael@linux</href>'})
        basic='mgr:mgrpw'
        result = self.publish('/file', basic,
                              env = {'REQUEST_METHOD': 'LOCK',
                                     'CONTENT-LENGTH': len(body)},
                              request_body = body)
        respbody = result.getBody()
        self.assertEqual(result.getStatus(), 200)

        ## ILockable doesn't work in this context.
        file = zapi.traverse(self.getRootFolder(), '/file')
        lock = self.storage.getLock(file)
        self.assert_(lock is not None)

    def test_lock_file(self):
        file = File('some content', 'text/plain')
        self.getRootFolder()['file'] = file
        self.commit()

        body = makeLockBody(
            {'locktype': 'write',
             'lockscope': 'exclusive',
             'owner': '<href>mailto:michael@linux</href>'})
        basic='mgr:mgrpw'
        result = self.publish('/file', basic,
                              env = {'REQUEST_METHOD': 'LOCK',
                                     'CONTENT-LENGTH': len(body),
                                     },
                              request_body = body)
        respbody = result.getBody()

        token = result.getHeader('lock-token')
        result = self.publish('/file', basic,
                              env = {'REQUEST_METHOD': 'LOCK',
                                     'CONTENT-LENGTH': 0,
                                     'TIMEOUT': 'Second-1400',
                                     'IF': '(%s)' % token,
                                     },
                              )
        respbody = result.getBody()
        xmlresp = minidom.parseString(respbody)
        timeout = xmlresp.getElementsByTagNameNS('DAV:', 'timeout')
        self.assertEqual(len(timeout), 1)
        self.assertEqual(timeout[0].toxml(), u'<timeout>Second-1400</timeout>')

        token = result.getHeader('lock-token')
        result = self.publish('/file', basic,
                              env = {'REQUEST_METHOD': 'LOCK',
                                     'CONTENT-LENGTH': 0,
                                     'TIMEOUT': 'Second-1400',
                                     'IF': '(<xxx>)',
                                     },
                              )
        respbody = result.getBody()
        self.assertEqual(result.getStatus(), 412)


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestAllowBefore))
    suite.addTest(makeSuite(TestLOCK))
    suite.addTest(makeSuite(TestAllowAfter))

    return suite

if __name__ == '__main__':
    main(defaultTest = 'test_suite')
