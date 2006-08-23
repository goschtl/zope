##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Test WebDAV propfind method.

$Id$
"""

import unittest
from cStringIO import StringIO
import UserDict
import datetime
import random
import time

from zope import interface
from zope import schema
import zope.schema.interfaces
from zope import component
from zope.security.proxy import removeSecurityProxy
from zope.traversing.api import getPath, traverse, getRoot
from zope.traversing.interfaces import IContainmentRoot
from zope.location.traversing import LocationPhysicallyLocatable
from zope.app.container.interfaces import IReadContainer
from zope.webdav.locking import DEFAULTTIMEOUT, MAXTIMEOUT
from zope.webdav.locking import UNLOCKMethod, LOCKMethod
from zope.webdav.testing import etreeSetup, etreeTearDown, assertXMLEqual
import zope.webdav.publisher
import zope.webdav.interfaces

_randGen = random.Random(time.time())

class TestWebDAVRequest(zope.webdav.publisher.WebDAVRequest):

    def __init__(self, lockinfo = {}, body = "", environ = {}):
        env = environ.copy()

        if body:
            env.setdefault("CONTENT_TYPE", "text/xml")
        env.setdefault("CONTENT_LENGTH", len(body))

        super(TestWebDAVRequest, self).__init__(StringIO(body), env)

        self.processInputs()


class LOCKINGHeaders(unittest.TestCase):

    def test_depth_empty(self):
        lock = LOCKMethod(None, TestWebDAVRequest())
        self.assertEqual(lock.getDepth(), "infinity")

    def test_depth_zero(self):
        lock = LOCKMethod(None, TestWebDAVRequest(environ = {"DEPTH": "0"}))
        self.assertEqual(lock.getDepth(), "0")

    def test_timeout_default(self):
        lock = LOCKMethod(None, TestWebDAVRequest(environ = {}))
        self.assertEqual(lock.getTimeout(),
                         datetime.timedelta(seconds = DEFAULTTIMEOUT))

    def test_timeout_infinity(self):
        request = TestWebDAVRequest(environ = {"TIMEOUT": "infinity"})
        lock = LOCKMethod(None, request)
        self.assertEqual(lock.getTimeout(),
                         datetime.timedelta(seconds = DEFAULTTIMEOUT))

    def test_timeout_second_500(self):
        request = TestWebDAVRequest(environ = {"TIMEOUT": "Second-500"})
        lock = LOCKMethod(None, request)
        self.assertEqual(lock.getTimeout(),
                         datetime.timedelta(seconds = 500))

    def test_invalid_second(self):
        request = TestWebDAVRequest(environ = {"TIMEOUT": "XXX-500"})
        lock = LOCKMethod(None, request)
        self.assertRaises(zope.webdav.interfaces.BadRequest, lock.getTimeout)

    def test_invalid_second_value(self):
        request = TestWebDAVRequest(environ = {"TIMEOUT": "Second-500x"})
        lock = LOCKMethod(None, request)
        self.assertRaises(zope.webdav.interfaces.BadRequest, lock.getTimeout)

    def test_big_second(self):
        request = TestWebDAVRequest(
            environ = {"TIMEOUT": "Second-%d" %(MAXTIMEOUT + 100)})
        lock = LOCKMethod(None, request)
        self.assertEqual(lock.getTimeout(),
                         datetime.timedelta(seconds = DEFAULTTIMEOUT))


class DAVLockmanager(object):
    interface.implements(zope.webdav.interfaces.IDAVLockmanager)

    def __init__(self, context):
        self.context = context

    def generateLocktoken(self):
        return "opaquelocktoken:%s-%s-00105A989226:%.03f" % \
               (_randGen.random(), _randGen.random(), time.time())

    def lock(self, scope, type, owner, duration, depth,
             context = None):
        if context is None:
            if self.islockedObject(self.context):
                raise zope.webdav.interfaces.AlreadyLocked(self.context)

            ob = removeSecurityProxy(self.context)
            setattr(ob, "_is_locked", {"scope": scope,
                                       "type": type,
                                       "owner": owner,
                                       "duration": duration,
                                       "depth": depth,
                                       "token": self.generateLocktoken(),
                                       "indirectlylocked": [],
                                       "lockroot": getPath(self.context)})
        else:
            if self.islockedObject(context):
                raise zope.webdav.interfaces.AlreadyLocked(context)

            ob = removeSecurityProxy(context)
            setattr(ob, "_is_indirectly_locked",
                    {"lockroot": getPath(self.context),
                     "rootinfo": removeSecurityProxy(self.context)._is_locked,
                     })
            root = removeSecurityProxy(self.context)
            root._is_locked["indirectlylocked"].append(getPath(ob))

        if context is None:
            context = self.context

        if depth == "infinity" and IReadContainer.providedBy(context):
            for subob in context.values():
                self.lock(scope, type, owner, duration, depth, subob)

    def getActivelock(self, request = None):
        return getActiveLock(self.context, request)

    def refreshlock(self, timeout):
        if not self.islockedObject(self.context):
            raise zope.webdav.interfaces.ConflictError(
                self.context, u"The context is not locked")

        ob = removeSecurityProxy(self.context)
        root = getRoot(self.context)

        if getattr(ob, "_is_indirectly_locked", None) is not None:
            lockroot = traverse(root, ob._is_indirectly_locked["lockroot"])
        else:
            lockroot = ob

        removeSecurityProxy(lockroot)._is_locked["duration"] = timeout

    def unlock(self):
        if not self.islockedObject(self.context):
            raise Exception("object is not locked")

        ob = removeSecurityProxy(self.context)
        root = getRoot(self.context)

        if getattr(ob, "_is_indirectly_locked", None) is not None:
            lockroot = traverse(root, ob._is_indirectly_locked["lockroot"])
        else:
            lockroot = ob

        lockroot = removeSecurityProxy(lockroot)
        for path in lockroot._is_locked["indirectlylocked"]:
            ob = removeSecurityProxy(traverse(root, path))
            delattr(ob, "_is_indirectly_locked")
        delattr(lockroot, "_is_locked")

    def islocked(self):
        return self.islockedObject(self.context)

    def islockedObject(self, context):
        ob = removeSecurityProxy(context)
        return getattr(ob, "_is_locked", None) is not None or \
               getattr(ob, "_is_indirectly_locked", None) is not None


@interface.implementer(zope.webdav.coreproperties.IActiveLock)
def getActiveLock(context, request):
    ob = removeSecurityProxy(context)

    data = getattr(ob, "_is_indirectly_locked", None)
    if data is not None:
        root = traverse(getRoot(context), data["lockroot"])
        root = removeSecurityProxy(root)
        return ActiveLock(root._is_locked)

    data = getattr(ob, "_is_locked", None)
    if data is not None:
        return ActiveLock(data)

    return None


class ActiveLock(object):
    interface.implements(zope.webdav.coreproperties.IActiveLock)

    def __init__(self, data):
        self.data = data

    @property
    def lockscope(self):
        return [u"exclusive"]

    @property
    def locktype(self):
        return [u"write"]

    @property
    def depth(self):
        return self.data["depth"]

    @property
    def owner(self):
        return self.data["owner"]

    @property
    def timeout(self):
        seconds = self.data["duration"]
        if not isinstance(seconds, int):
            seconds = seconds.seconds
        return u"Second-%d" % seconds

    @property
    def locktoken(self):
        return [self.data["token"]]

    @property
    def lockroot(self):
        return "http://localhost%s" % self.data["lockroot"]


class Lockdiscovery(object):
    interface.implements(zope.webdav.coreproperties.IDAVLockdiscovery)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def lockdiscovery(self):
        activelock = getActiveLock(self.context, self.request)
        if activelock is not None:
            return [activelock]
        return None


class IResource(interface.Interface):

    text = schema.TextLine(
        title = u"Example Text Property")

    intprop = schema.Int(
        title = u"Example Int Property")


class Resource(object):
    interface.implements(IResource)

    def __init__(self, text = u"", intprop = 0):
        self.text = text
        self.intprop = intprop


class ICollectionResource(IReadContainer):

    title = schema.TextLine(
        title = u"Title",
        description = u"Title of resource")


class CollectionResource(UserDict.UserDict):
    interface.implements(ICollectionResource)

    title = None

    def __setitem__(self, key, val):
        val.__parent__ = self
        val.__name__ = key

        self.data[key] = val

class RootCollectionResource(CollectionResource):
    interface.implements(IContainmentRoot)


class LOCKTestCase(unittest.TestCase):

    def setUp(self):
        etreeSetup()

        self.root = RootCollectionResource()

        gsm = component.getGlobalSiteManager()
        gsm.registerAdapter(DAVLockmanager, (IResource,))
        gsm.registerAdapter(DAVLockmanager, (ICollectionResource,))
        gsm.registerAdapter(LocationPhysicallyLocatable, (IResource,))
        gsm.registerAdapter(LocationPhysicallyLocatable, (ICollectionResource,))

        gsm.registerAdapter(Lockdiscovery,
                            (IResource, zope.webdav.interfaces.IWebDAVRequest))
        gsm.registerUtility(zope.webdav.coreproperties.lockdiscovery,
                            name = "{DAV:}lockdiscovery")
        gsm.registerAdapter(getActiveLock,
                            (IResource, zope.webdav.interfaces.IWebDAVRequest))

        gsm.registerAdapter(zope.webdav.widgets.TextDAVWidget,
                            (zope.schema.interfaces.IText,
                             zope.webdav.interfaces.IWebDAVRequest))
        gsm.registerAdapter(zope.webdav.widgets.TextDAVWidget,
                            (zope.schema.interfaces.IURI,
                             zope.webdav.interfaces.IWebDAVRequest))
        gsm.registerAdapter(zope.webdav.properties.OpaqueWidget,
                            (zope.webdav.properties.DeadField,
                             zope.webdav.interfaces.IWebDAVRequest))
        gsm.registerAdapter(zope.webdav.widgets.ListDAVWidget,
                            (zope.schema.interfaces.IList,
                             zope.webdav.interfaces.IWebDAVRequest))
        gsm.registerAdapter(zope.webdav.widgets.ObjectDAVWidget,
                            (zope.schema.interfaces.IObject,
                             zope.webdav.interfaces.IWebDAVRequest))

    def tearDown(self):
        etreeTearDown()

        gsm = component.getGlobalSiteManager()
        gsm.unregisterAdapter(DAVLockmanager, (IResource,))
        gsm.unregisterAdapter(DAVLockmanager, (ICollectionResource,))
        gsm.unregisterAdapter(LocationPhysicallyLocatable, (IResource,))
        gsm.unregisterAdapter(
            LocationPhysicallyLocatable, (ICollectionResource,))

        del self.root

    def test_handleLock_notlockinfo(self):
        body = """<?xml version="1.0" encoding="utf-8" ?>
<D:notlockinfo xmlns:D="DAV:">
  Not a lockinfo.
</D:notlockinfo>"""
        request = TestWebDAVRequest(body = body)

        lock = LOCKMethod(None, request)
        self.assertRaises(
            zope.webdav.interfaces.UnprocessableError, lock.handleLock)

    def test_handleLock_invalidDepth(self):
        body = """<?xml version="1.0" encoding="utf-8" ?>
<D:lockinfo xmlns:D="DAV:">
  Not a lockinfo.
</D:lockinfo>"""
        request = TestWebDAVRequest(body = body, environ = {"DEPTH": "1"})

        lock = LOCKMethod(None, request)
        self.assertRaises(
            zope.webdav.interfaces.BadRequest, lock.handleLock)

    def test_handleLock_nolockscope(self):
        body = """<?xml version="1.0" encoding="utf-8" ?>
<D:lockinfo xmlns:D="DAV:">
  Not a lockinfo.
</D:lockinfo>"""
        request = TestWebDAVRequest(body = body)

        lock = LOCKMethod(None, request)
        self.assertRaises(
            zope.webdav.interfaces.UnprocessableError, lock.handleLock)

    def test_handleLock_nolocktype(self):
        body = """<?xml version="1.0" encoding="utf-8" ?>
<D:lockinfo xmlns:D="DAV:">
  <D:lockscope><D:exculsive/></D:lockscope>
</D:lockinfo>"""
        request = TestWebDAVRequest(body = body)

        lock = LOCKMethod(None, request)
        self.assertRaises(
            zope.webdav.interfaces.UnprocessableError, lock.handleLock)

    def test_handleLock(self):
        body = """<?xml version="1.0" encoding="utf-8" ?>
<D:lockinfo xmlns:D="DAV:">
  <D:lockscope><D:exclusive/></D:lockscope>
  <D:locktype><D:write/></D:locktype>
  <D:owner>
    <D:href>http://example.org/~ejw/contact.html</D:href>
  </D:owner>
</D:lockinfo>"""
        request = TestWebDAVRequest(body = body)
        resource = self.root["resource"] = Resource()

        lock = LOCKMethod(resource, request)
        errors = lock.handleLock()

        lockmanager = DAVLockmanager(resource)
        self.assertEqual(lockmanager.islocked(), True)

    def test_handleLock_alreadLocked(self):
        body = """<?xml version="1.0" encoding="utf-8" ?>
<D:lockinfo xmlns:D="DAV:">
  <D:lockscope><D:exclusive/></D:lockscope>
  <D:locktype><D:write/></D:locktype>
  <D:owner>
    <D:href>http://example.org/~ejw/contact.html</D:href>
  </D:owner>
</D:lockinfo>"""
        request = TestWebDAVRequest(body = body)
        resource = self.root["resource"] = Resource()

        lock = LOCKMethod(resource, request)
        errors = lock.handleLock()
        self.assertEqual(errors, [])

        lockmanager = DAVLockmanager(resource)
        self.assertEqual(lockmanager.islocked(), True)

        lock = LOCKMethod(resource, request)
        errors = lock.handleLock()
        self.assertEqual(len(errors), 1)
        self.assert_(zope.webdav.interfaces.IAlreadyLocked.providedBy(errors[0]))

    def test_handleLockRefresh_notlocked(self):
        request = TestWebDAVRequest()
        resource = self.root["resource"] = Resource()

        lock = LOCKMethod(resource, request)

        self.assertRaises(zope.webdav.interfaces.PreconditionFailed,
                          lock.handleLockRefresh)

    def test_handleLockRefresh_noifheader(self):
        request = TestWebDAVRequest()
        resource = self.root["resource"] = Resource()

        lock = LOCKMethod(resource, request)
        lockmanager = DAVLockmanager(resource)
        lockmanager.lock(u"exclusive", u"write", u"Michael",
                         duration = datetime.timedelta(seconds = 100),
                         depth = "0")

        self.assertRaises(zope.webdav.interfaces.PreconditionFailed,
                          lock.handleLockRefresh)

    def test_handleLockRefresh_ifbadheader(self):
        request = TestWebDAVRequest(environ = {"IF": "<xxx>"})
        resource = self.root["resource"] = Resource()

        lock = LOCKMethod(resource, request)
        lockmanager = DAVLockmanager(resource)
        lockmanager.lock(u"exclusive", u"write", u"Michael",
                         duration = datetime.timedelta(seconds = 100),
                         depth = "0")

        self.assertRaises(zope.webdav.interfaces.PreconditionFailed,
                          lock.handleLockRefresh)

    def test_handleLockRefresh_ifbadheader2(self):
        request = TestWebDAVRequest(environ = {"IF": "xxx"})
        resource = self.root["resource"] = Resource()

        lock = LOCKMethod(resource, request)
        lockmanager = DAVLockmanager(resource)
        lockmanager.lock(u"exclusive", u"write", u"Michael",
                         duration = datetime.timedelta(seconds = 100),
                         depth = "0")

        self.assertRaises(zope.webdav.interfaces.PreconditionFailed,
                          lock.handleLockRefresh)

    def test_handleLockRefresh_defaulttimeout(self):
        request = TestWebDAVRequest(environ = {"IF": "xxx"})
        resource = self.root["resource"] = Resource()

        lock = LOCKMethod(resource, request)
        lockmanager = DAVLockmanager(resource)
        lockmanager.lock(u"exclusive", u"write", u"Michael",
                         duration = datetime.timedelta(seconds = 100),
                         depth = "0")

        self.assertEqual(lockmanager.getActivelock().timeout,
                         u"Second-100")

        locktoken = lockmanager.getActivelock().locktoken[0]
        request = TestWebDAVRequest(environ = {"IF": "<%s>" % locktoken})
        lock = LOCKMethod(resource, request)

        lock.handleLockRefresh()

        self.assertEqual(lockmanager.getActivelock().timeout,
                         u"Second-720")

    def test_handleLockRefresh_timeout(self):
        request = TestWebDAVRequest(environ = {"IF": "xxx"})
        resource = self.root["resource"] = Resource()

        lock = LOCKMethod(resource, request)
        lockmanager = DAVLockmanager(resource)
        lockmanager.lock(u"exclusive", u"write", u"Michael",
                         duration = datetime.timedelta(seconds = 100),
                         depth = "0")

        self.assertEqual(lockmanager.getActivelock().timeout,
                         u"Second-100")

        locktoken = lockmanager.getActivelock().locktoken[0]
        request = TestWebDAVRequest(environ = {"IF": "<%s>" % locktoken,
                                               "TIMEOUT": "Second-500"})
        lock = LOCKMethod(resource, request)

        lock.handleLockRefresh()

        self.assertEqual(lockmanager.getActivelock().timeout,
                         u"Second-500")

    def test_lock_alreadLocked(self):
        body = """<?xml version="1.0" encoding="utf-8" ?>
<D:lockinfo xmlns:D="DAV:">
  <D:lockscope><D:exclusive/></D:lockscope>
  <D:locktype><D:write/></D:locktype>
  <D:owner>
    <D:href>http://example.org/~ejw/contact.html</D:href>
  </D:owner>
</D:lockinfo>"""
        request = TestWebDAVRequest(body = body)
        resource = self.root["resource"] = Resource()

        lockmanager = DAVLockmanager(resource)
        lockmanager.lock(u"exclusive", u"write", u"Michael",
                         duration = datetime.timedelta(seconds = 100),
                         depth = "0")

        lock = LOCKMethod(resource, request)
        self.assertRaises(zope.webdav.interfaces.WebDAVErrors, lock.LOCK)

    def test_lock(self):
        body = """<?xml version="1.0" encoding="utf-8" ?>
<D:lockinfo xmlns:D="DAV:">
  <D:lockscope><D:exclusive/></D:lockscope>
  <D:locktype><D:write/></D:locktype>
  <D:owner>
    <D:href>http://example.org/~ejw/contact.html</D:href>
  </D:owner>
</D:lockinfo>"""
        request = TestWebDAVRequest(body = body)
        resource = self.root["resource"] = Resource()

        lock = LOCKMethod(resource, request)
        result = lock.LOCK()

        locktoken = request.response.getHeader("lock-token")
        lockmanager = DAVLockmanager(resource)
        currentlocktoken = lockmanager.getActivelock().locktoken[0]
        self.assert_(locktoken[0], "<")
        self.assert_(locktoken[-1], ">")
        self.assertEqual(currentlocktoken, locktoken[1:-1])

        assertXMLEqual(result, """<ns0:prop xmlns:ns0="DAV:">
<ns0:lockdiscovery xmlns:ns0="DAV:">
  <ns0:activelock xmlns:ns0="DAV:">
    <ns0:lockscope xmlns:ns0="DAV:"><ns0:exclusive xmlns:ns0="DAV:"/></ns0:lockscope>
    <ns0:locktype xmlns:ns0="DAV:"><ns0:write xmlns:ns0="DAV:"/></ns0:locktype>
    <ns0:depth xmlns:ns0="DAV:">infinity</ns0:depth>
    <ns0:owner xmlns:D="DAV:">
      <ns0:href>http://example.org/~ejw/contact.html</ns0:href>
    </ns0:owner>
    <ns0:timeout xmlns:ns0="DAV:">Second-720</ns0:timeout>
    <ns0:locktoken xmlns:ns0="DAV:">
      <ns0:href xmlns:ns0="DAV:">%s</ns0:href>
    </ns0:locktoken>
    <ns0:lockroot xmlns:ns0="DAV:">http://localhost/resource</ns0:lockroot>
  </ns0:activelock>
</ns0:lockdiscovery></ns0:prop>""" % locktoken[1:-1])

    def test_refreshlock_alreadLocked(self):
        request = TestWebDAVRequest()
        resource = self.root["resource"] = Resource()

        lockmanager = DAVLockmanager(resource)
        lockmanager.lock(u"exclusive", u"write", u"Michael",
                         duration = datetime.timedelta(seconds = 100),
                         depth = "0")

        lock = LOCKMethod(resource, request)
        self.assertRaises(zope.webdav.interfaces.PreconditionFailed, lock.LOCK)

    def test_refreshlock(self):
        resource = self.root["resource"] = Resource()

        lockmanager = DAVLockmanager(resource)
        lockmanager.lock(u"exclusive", u"write",
                         u"""<D:owner xmlns:D="DAV:">Michael</D:owner>""",
                         duration = datetime.timedelta(seconds = 100),
                         depth = "0")
        locktoken = lockmanager.getActivelock().locktoken[0]

        request = TestWebDAVRequest(environ = {"IF": "<%s>" % locktoken})
        lock = LOCKMethod(resource, request)
        result = lock.LOCK()

        assertXMLEqual(result, """<ns0:prop xmlns:ns0="DAV:">
<ns0:lockdiscovery xmlns:ns0="DAV:">
  <ns0:activelock xmlns:ns0="DAV:">
    <ns0:lockscope xmlns:ns0="DAV:"><ns0:exclusive xmlns:ns0="DAV:"/></ns0:lockscope>
    <ns0:locktype xmlns:ns0="DAV:"><ns0:write xmlns:ns0="DAV:"/></ns0:locktype>
    <ns0:depth xmlns:ns0="DAV:">0</ns0:depth>
    <ns0:owner xmlns:D="DAV:">Michael</ns0:owner>
    <ns0:timeout xmlns:ns0="DAV:">Second-720</ns0:timeout>
    <ns0:locktoken xmlns:ns0="DAV:">
      <ns0:href xmlns:ns0="DAV:">%s</ns0:href>
    </ns0:locktoken>
    <ns0:lockroot xmlns:ns0="DAV:">http://localhost/resource</ns0:lockroot>
  </ns0:activelock>
</ns0:lockdiscovery></ns0:prop>""" % locktoken)

    def test_unlock_nolocktoken(self):
        resource = self.root["resource"] = Resource()

        lockmanager = DAVLockmanager(resource)
        lockmanager.lock(u"exclusive", u"write",
                         u"""<D:owner xmlns:D="DAV:">Michael</D:owner>""",
                         duration = datetime.timedelta(seconds = 100),
                         depth = "0")

        unlock = UNLOCKMethod(resource, TestWebDAVRequest())
        self.assertRaises(zope.webdav.interfaces.BadRequest, unlock.UNLOCK)

    def test_unlock_badlocktoken(self):
        resource = self.root["resource"] = Resource()

        lockmanager = DAVLockmanager(resource)
        lockmanager.lock(u"exclusive", u"write",
                         u"""<D:owner xmlns:D="DAV:">Michael</D:owner>""",
                         duration = datetime.timedelta(seconds = 100),
                         depth = "0")

        request = TestWebDAVRequest(environ = {"LOCK_TOKEN": "XXX"})
        unlock = UNLOCKMethod(resource, request)
        self.assertRaises(zope.webdav.interfaces.ConflictError, unlock.UNLOCK)

    def test_unlock_badlocktoken2(self):
        resource = self.root["resource"] = Resource()

        lockmanager = DAVLockmanager(resource)
        lockmanager.lock(u"exclusive", u"write",
                         u"""<D:owner xmlns:D="DAV:">Michael</D:owner>""",
                         duration = datetime.timedelta(seconds = 100),
                         depth = "0")

        request = TestWebDAVRequest(environ = {"LOCK_TOKEN": "<XXX>"})
        unlock = UNLOCKMethod(resource, request)
        self.assertRaises(zope.webdav.interfaces.ConflictError, unlock.UNLOCK)

    def test_unlock(self):
        resource = self.root["resource"] = Resource()

        lockmanager = DAVLockmanager(resource)
        lockmanager.lock(u"exclusive", u"write",
                         u"""<D:owner xmlns:D="DAV:">Michael</D:owner>""",
                         duration = datetime.timedelta(seconds = 100),
                         depth = "0")
        locktoken = lockmanager.getActivelock().locktoken[0]

        request = TestWebDAVRequest(
            environ = {"LOCK_TOKEN": "<%s>" % locktoken})
        unlock = UNLOCKMethod(resource, request)
        result = unlock.UNLOCK()

        self.assertEqual(result, "")
        self.assertEqual(request.response.getStatus(), 204)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(LOCKINGHeaders),
        unittest.makeSuite(LOCKTestCase),
        ))
