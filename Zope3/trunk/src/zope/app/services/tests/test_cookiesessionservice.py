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

from unittest import TestCase, TestLoader, TextTestRunner
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.component import getServiceManager, getService
from zope.server.http.http_date import parse_http_date

from zope.app.interfaces.services.session import ISessionService
from zope.app.interfaces.services.session import ISessionDataManager
from zope.app.services.session import CookieSessionService
from zope.interface import implements

import time

class DummyDataManager:

    implements(ISessionDataManager)

    def __init__(self):
        self.data = {}

    def getDataObject(self, sid):
        return self.data.setdefault(sid, {})

    def deleteData(self, sid):
        del self.data[sid]

class FakeRequest:

    def __init__(self):
        self.sets = 0
        self.cookies = {}
        # This class implements methods of the response too.
        self.response = self

    def setCookie(self, k, v, **kw):
        # This is actually a method on the response.
        self.sets += 1
        self.cookies[k] = v
        if (not abs(parse_http_date(kw["expires"]) - int(time.time()) - 1800)
            < 3):
            raise AssertionError

    def getCookie(self, name, default=None):
        # This is actually a method on the reponse.
        value = self.cookies.get(name)
        if value is None:
            return default
        return {'value':value}

    def getApplicationURL(self, depth=0, path_only=False):
        if depth == 0 and path_only:
            return '/'
        raise AssertionError(
            'Inappropriate arguments passed to getApplicationURL')


class SessionServiceTestCaseMixin(PlacefulSetup):

    serviceFactory = None

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.buildFolders()
        root_sm = getServiceManager(None)
        svc = self.serviceFactory()
        root_sm.defineService("Sessions", ISessionService)
        root_sm.provideService("Sessions", svc)
        self.svc = getService(self.rootFolder, "Sessions")

    def testRegister(self):
        d = DummyDataManager()
        d2 = DummyDataManager()
        self.svc.registerDataManager("foo", d)
        self.assertRaises(ValueError, self.svc.registerDataManager, "foo", d2)
        self.assertEquals(self.svc.getDataManager("foo"), d)
        self.svc.unregisterDataManager("foo")
        self.assertRaises(KeyError, self.svc.getDataManager, "foo")
        self.svc.registerDataManager("foo", d2)

    def testCookie(self):
        req = FakeRequest()
        sid = self.svc.generateUniqueId()
        self.svc.setRequestId(req, sid)
        self.assertEquals(self.svc.getRequestId(req), sid)

    def testGetSession(self):
        req = FakeRequest()
        sid = self.svc.getSessionId(req)
        self.assertEquals(req.sets, 1)
        self.assertEquals(self.svc.getRequestId(req), sid)
        self.assertEquals(self.svc.getSessionId(req), sid)
        # make sure cookie was also set during 2nd getSessionId
        self.assertEquals(req.sets, 2)

    def testLookupAndInvalidate(self):
        dm = DummyDataManager()
        svc = self.svc
        svc.registerDataManager("dm", dm)
        req = FakeRequest()
        from zope.app.services.session import getSessionDataObject
        d = getSessionDataObject(self.rootFolder, req, "dm")
        d["a"] = "b"
        self.assert_(d is dm.getDataObject(svc.getSessionId(req)))
        self.assertEquals("b", dm.getDataObject(svc.getSessionId(req))["a"])
        svc.invalidate(svc.getSessionId(req))
        d2 = getSessionDataObject(self.rootFolder, req, "dm")
        self.assertEquals(d2, {})

    def testForgingCookies(self):
        for fakeValue in ["dsada", "2" * 54]:
            req = FakeRequest()
            self.svc.setRequestId(req, fakeValue)
            self.assertEquals(self.svc.getRequestId(req), None)


class CookieServiceTestCase(SessionServiceTestCaseMixin, TestCase):

    serviceFactory = CookieSessionService


def test_suite():
    loader = TestLoader()
    return loader.loadTestsFromTestCase(CookieServiceTestCase)

if __name__=='__main__':
    TextTestRunner().run(test_suite())

