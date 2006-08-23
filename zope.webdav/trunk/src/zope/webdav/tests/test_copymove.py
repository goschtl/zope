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
"""Test WebDAV COPY and MOVE methods.

$Id$
"""

import unittest
from cStringIO import StringIO

from zope import interface
from zope import component
from zope.copypastemove.interfaces import IObjectCopier, IObjectMover
from zope.location.traversing import LocationPhysicallyLocatable
from zope.traversing.adapters import Traverser, DefaultTraversable
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.app.publication.http import MethodNotAllowed
from zope.traversing.interfaces import IContainmentRoot

import zope.webdav.publisher
from zope.webdav.copymove import COPY, MOVE

import test_locking

class TestRequest(zope.webdav.publisher.WebDAVRequest):

    def __init__(self, environ = {}):
        env = environ.copy()
        env.setdefault("HTTP_HOST", "localhost")
        super(TestRequest, self).__init__(StringIO(""), env)

        self.processInputs()


def baseSetUp():
    gsm = component.getGlobalSiteManager()
    gsm.registerAdapter(LocationPhysicallyLocatable,
                        (test_locking.IResource,))
    gsm.registerAdapter(LocationPhysicallyLocatable,
                        (test_locking.ICollectionResource,))
    gsm.registerAdapter(Traverser, (test_locking.IResource,))
    gsm.registerAdapter(Traverser, (test_locking.ICollectionResource,))
    gsm.registerAdapter(DefaultTraversable, (test_locking.IResource,))
    gsm.registerAdapter(DefaultTraversable,
                        (test_locking.ICollectionResource,))


def baseTearDown():
    gsm = component.getGlobalSiteManager()
    gsm.unregisterAdapter(LocationPhysicallyLocatable,
                          (test_locking.IResource,))
    gsm.unregisterAdapter(LocationPhysicallyLocatable,
                          (test_locking.ICollectionResource,))
    gsm.unregisterAdapter(Traverser, (test_locking.IResource,))
    gsm.unregisterAdapter(Traverser, (test_locking.ICollectionResource,))
    gsm.unregisterAdapter(DefaultTraversable, (test_locking.IResource,))
    gsm.unregisterAdapter(DefaultTraversable,
                          (test_locking.ICollectionResource,))


class COPYMOVEParseHeadersTestCase(unittest.TestCase):

    def setUp(self):
        self.root = test_locking.RootCollectionResource()

        baseSetUp()

    def tearDown(self):
        del self.root

        baseTearDown()

    def test_no_overwrite(self):
        request = TestRequest()
        copy = COPY(None, request)

        self.assertEqual(copy.getOverwrite(), True)

    def test_T_overwrite(self):
        request = TestRequest(environ = {"OVERWRITE": "t"})
        copy = COPY(None, request)

        self.assertEqual(copy.getOverwrite(), True)

    def test_t_overwrite(self):
        request = TestRequest(environ = {"OVERWRITE": "T"})
        copy = COPY(None, request)

        self.assertEqual(copy.getOverwrite(), True)

    def test_F_overwrite(self):
        request = TestRequest(environ = {"OVERWRITE": "F"})
        copy = COPY(None, request)

        self.assertEqual(copy.getOverwrite(), False)

    def test_f_overwrite(self):
        request = TestRequest(environ = {"OVERWRITE": "f"})
        copy = COPY(None, request)

        self.assertEqual(copy.getOverwrite(), False)

    def test_bad_overwrite(self):
        request = TestRequest(environ = {"OVERWRITE": "x"})
        copy = COPY(None, request)

        self.assertRaises(zope.webdav.interfaces.BadRequest, copy.getOverwrite)

    def test_default_destination_path(self):
        request = TestRequest()
        copy = COPY(None, request)

        self.assertRaises(
            zope.webdav.interfaces.BadRequest, copy.getDestinationPath)

    def test_destination_path(self):
        request = TestRequest(
            environ = {"DESTINATION": "http://localhost/testpath"})
        copy = COPY(None, request)

        self.assertEqual(copy.getDestinationPath(), "/testpath")

    def test_destination_path_slash(self):
        request = TestRequest(
            environ = {"DESTINATION": "http://localhost/testpath/"})
        copy = COPY(None, request)

        self.assertEqual(copy.getDestinationPath(), "/testpath")

    def test_getDestinationPath_wrong_server(self):
        request = TestRequest(
            environ = {"DESTINATION": "http://www.server.com/testpath"})
        copy = COPY(None, request)

        self.assertRaises(zope.webdav.interfaces.BadGateway,
                          copy.getDestinationPath)

    def test_getDestinationNameAndParentObject(self):
        resource = self.root["resource"] = test_locking.Resource()
        request = TestRequest(
            environ = {"DESTINATION": "http://localhost/testpath"})

        copy = COPY(resource, request)
        destname, destob, parent = copy.getDestinationNameAndParentObject()
        self.assertEqual(destname, "testpath")
        self.assertEqual(destob, None)
        self.assertEqual(parent, self.root)

    def test_getDestinationNameAndParentObject_destob_overwrite(self):
        destresource = self.root["destresource"] = test_locking.Resource()
        resource = self.root["resource"] = test_locking.Resource()
        request = TestRequest(
            environ = {"DESTINATION": "http://localhost/destresource",
                       "OVERWRITE": "T"})

        copy = COPY(resource, request)
        destname, destob, parent = copy.getDestinationNameAndParentObject()
        self.assertEqual(destname, "destresource")
        self.assertEqual(destob, destresource)
        self.assert_("destresource" not in self.root)
        self.assertEqual(parent, self.root)

    def test_getDestinationNameAndParentObject_destob_overwrite_failed(self):
        destresource = self.root["destresource"] = test_locking.Resource()
        resource = self.root["resource"] = test_locking.Resource()
        request = TestRequest(
            environ = {"DESTINATION": "http://localhost/destresource",
                       "OVERWRITE": "F"})

        copy = COPY(resource, request)
        self.assertRaises(zope.webdav.interfaces.PreconditionFailed,
                          copy.getDestinationNameAndParentObject)
        self.assert_("destresource" in self.root)

    def test_getDestinationNameAndParentObject_noparent(self):
        resource = self.root["resource"] = test_locking.Resource()
        request = TestRequest(
            environ = {"DESTINATION": "http://localhost/noparent/testpath"})

        copy = COPY(resource, request)
        self.assertRaises(zope.webdav.interfaces.ConflictError,
                          copy.getDestinationNameAndParentObject)

    def test_getDestinationNameAndParentObject_destob_sameob(self):
        resource = self.root["resource"] = test_locking.Resource()
        request = TestRequest(
            environ = {"DESTINATION": "http://localhost/resource",
                       "OVERWRITE": "T"})

        copy = COPY(resource, request)
        self.assertRaises(zope.webdav.interfaces.ForbiddenError,
                          copy.getDestinationNameAndParentObject)

    def test_nocopier(self):
        resource = self.root["resource"] = test_locking.Resource()
        request = TestRequest(
            environ = {"DESTINATION": "http://localhost/copy_of_resource"})

        copy = COPY(resource, request)
        self.assertRaises(MethodNotAllowed, copy.COPY)

    def test_nomovier(self):
        resource = self.root["resource"] = test_locking.Resource()
        request = TestRequest(
            environ = {"DESTINATION": "http://localhost/copy_of_resource"})

        copy = MOVE(resource, request)
        self.assertRaises(MethodNotAllowed, copy.MOVE)


class DummyResourceURL(object):
    interface.implements(IAbsoluteURL)

    def __init__(self, context, request):
        self.context = context

    def __str__(self):
        if getattr(self.context, "__parent__", None) is not None:
            path = DummyResourceURL(self.context.__parent__, None)()
        elif IContainmentRoot.providedBy(self.context):
            return ""
        else:
            path = ""

        if getattr(self.context, "__name__", None) is not None:
            path += "/" + self.context.__name__
        elif test_locking.IResource.providedBy(self.context):
            path += "/resource"
        elif test_locking.ICollectionResource.providedBy(self.context):
            path += "/collection"
        else:
            raise ValueError("unknown context type")

        return path

    __call__ = __str__


class Copier(object):
    interface.implements(IObjectCopier)

    iscopyable = True
    canCopyableTo = True

    def __init__(self, context):
        self.context = context

    def copyable(self):
        return self.iscopyable

    def copyTo(self, target, new_name):
        target[new_name] = self.context

        return new_name

    def copyableTo(self, parent, destname):
        return self.canCopyableTo


class COPYObjectTestCase(unittest.TestCase):

    def setUp(self):
        self.root = test_locking.RootCollectionResource()

        baseSetUp()

        Copier.iscopyable = True
        Copier.canCopyableTo = True
        gsm = component.getGlobalSiteManager()
        gsm.registerAdapter(Copier, (test_locking.IResource,))
        gsm.registerAdapter(DummyResourceURL,
                            (test_locking.IResource,
                             zope.webdav.interfaces.IWebDAVRequest))

    def tearDown(self):
        del self.root

        baseTearDown()

        gsm = component.getGlobalSiteManager()
        gsm.unregisterAdapter(Copier, (test_locking.IResource,))
        gsm.unregisterAdapter(DummyResourceURL,
                              (test_locking.IResource,
                               zope.webdav.interfaces.IWebDAVRequest))

    def test_copy(self):
        resource = self.root["resource"] = test_locking.Resource()
        request = TestRequest(
            environ = {"DESTINATION": "http://localhost/copy_of_resource"})

        copy = COPY(resource, request)
        result = copy.COPY()

        self.assertEqual(request.response.getStatus(), 201)
        self.assertEqual(request.response.getHeader("Location"),
                         "/copy_of_resource")
        self.assertEqual(result, "")
        self.assertEqual(self.root["copy_of_resource"] is resource, True)
        self.assertEqual(self.root["resource"] is resource, True)

    def test_copy_overwrite(self):
        resource = self.root["resource"] = test_locking.Resource()
        resource2 = self.root["resource2"] = test_locking.Resource()
        request = TestRequest(
            environ = {"DESTINATION": "http://localhost/resource2",
                       "OVERWRITE": "T"})

        copy = COPY(resource, request)
        result = copy.COPY()

        self.assertEqual(request.response.getStatus(), 204)
        self.assertEqual(result, "")
        self.assertEqual(self.root["resource"] is resource, True)
        self.assertEqual(self.root["resource2"] is resource, True)

    def test_copy_not_copyable(self):
        resource = self.root["resource"] = test_locking.Resource()
        request = TestRequest(
            environ = {"DESTINATION": "http://localhost/copy_of_resource"})

        Copier.iscopyable = False

        copy = COPY(resource, request)
        self.assertRaises(MethodNotAllowed, copy.COPY)

    def test_copy_not_copyableto(self):
        resource = self.root["resource"] = test_locking.Resource()
        request = TestRequest(
            environ = {"DESTINATION": "http://localhost/copy_of_resource"})

        Copier.canCopyableTo = False

        copy = COPY(resource, request)
        self.assertRaises(zope.webdav.interfaces.ConflictError, copy.COPY)


class Movier(object):
    interface.implements(IObjectMover)

    isMoveable = True
    isMoveableTo = True

    def __init__(self, context):
        self.context = context

    def moveTo(self, target, new_name):
        del self.context.__parent__[self.context.__name__]
        target[new_name] = self.context

        return new_name

    def moveable(self):
        return self.isMoveable

    def moveableTo(self, target, name = None):
        return self.isMoveableTo


class MOVEObjectTestCase(unittest.TestCase):

    def setUp(self):
        self.root = test_locking.RootCollectionResource()

        baseSetUp()

        Movier.isMoveable = True
        Movier.isMoveableTo = True
        gsm = component.getGlobalSiteManager()
        gsm.registerAdapter(Movier, (test_locking.IResource,))
        gsm.registerAdapter(DummyResourceURL,
                            (test_locking.IResource,
                             zope.webdav.interfaces.IWebDAVRequest))

    def tearDown(self):
        del self.root

        baseTearDown()

        gsm = component.getGlobalSiteManager()
        gsm.unregisterAdapter(Movier, (test_locking.IResource,))
        gsm.unregisterAdapter(DummyResourceURL,
                              (test_locking.IResource,
                               zope.webdav.interfaces.IWebDAVRequest))

    def test_move(self):
        resource = self.root["resource"] = test_locking.Resource()
        request = TestRequest(
            environ = {"DESTINATION": "http://localhost/copy_of_resource"})

        move = MOVE(resource, request)
        result = move.MOVE()

        self.assertEqual(request.response.getStatus(), 201)
        self.assertEqual(request.response.getHeader("Location"),
                         "/copy_of_resource")
        self.assertEqual("resource" not in self.root, True)
        self.assertEqual(self.root["copy_of_resource"], resource)

    def test_move_overwrite(self):
        resource = self.root["resource"] = test_locking.Resource()
        resource2 = self.root["resource2"] = test_locking.Resource()
        request = TestRequest(
            environ = {"DESTINATION": "http://localhost/resource2",
                       "OVERWRITE": "T"})

        move = MOVE(resource, request)
        result = move.MOVE()

        self.assertEqual(request.response.getStatus(), 204)
        self.assertEqual("resource" not in self.root, True)
        self.assertEqual(self.root["resource2"] is resource, True)

    def test_move_not_moveable(self):
        resource = self.root["resource"] = test_locking.Resource()
        request = TestRequest(
            environ = {"DESTINATION": "http://localhost/copy_of_resource"})

        Movier.isMoveable = False

        move = MOVE(resource, request)
        self.assertRaises(MethodNotAllowed, move.MOVE)

    def test_move_not_moveableTo(self):
        resource = self.root["resource"] = test_locking.Resource()
        request = TestRequest(
            environ = {"DESTINATION": "http://localhost/copy_of_resource"})

        Movier.isMoveableTo = False

        move = MOVE(resource, request)
        self.assertRaises(zope.webdav.interfaces.ConflictError, move.MOVE)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(COPYMOVEParseHeadersTestCase),
        unittest.makeSuite(COPYObjectTestCase),
        unittest.makeSuite(MOVEObjectTestCase),
        ))
