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
"""Common utilities needed for writing WebDAV functional tests.

XXX - This really needs some tidying up, also the setup should be moved to
a global setup method so that individual tests can call it if they need to.

$Id$
"""

from cStringIO import StringIO
from BTrees.OOBTree import OOBTree

import persistent
import transaction

from zope import interface
from zope import component
from zope import schema
from zope.publisher.http import status_reasons
from zope.app.testing.functional import HTTPTestCase, FunctionalTestSetup
from zope.security.proxy import removeSecurityProxy
from zope.app.folder.folder import Folder
import zope.app.folder.interfaces
from zope.app.file.file import File
from zope.app.publication.http import HTTPPublication
from zope.security.management import newInteraction, endInteraction
from zope.security.testing import Principal, Participation

import zope.webdav.interfaces
from zope.webdav.publisher import WebDAVRequest
from zope.webdav.ietree import IEtree
from zope.webdav.properties import DAVProperty
from zope.webdav.testing import assertXMLEqual
import zope.webdav.coreproperties


class IExamplePropertyStorage(interface.Interface):

    exampleintprop = schema.Int(
        title = u"Example Integer Property",
        description = u"")

    exampletextprop = schema.Text(
        title = u"Example Text Property",
        description = u"")

exampleIntProperty = DAVProperty("{DAVtest:}exampleintprop",
                                 IExamplePropertyStorage)

exampleTextProperty = DAVProperty("{DAVtest:}exampletextprop",
                                  IExamplePropertyStorage)


ANNOT_KEY = "EXAMPLE_PROPERTY"
class ExamplePropertyStorage(object):
    interface.implements(IExamplePropertyStorage)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _getproperty(name, default = None):
        def get(self):
            annots = getattr(removeSecurityProxy(self.context),
                             "exampleannots", {})
            return annots.get("%s_%s" %(ANNOT_KEY, name), default)
        def set(self, value):
            annots = getattr(removeSecurityProxy(self.context),
                             "exampleannots", None)
            if annots is None:
                annots = removeSecurityProxy(
                    self.context).exampleannots = OOBTree()
            annots["%s_%s" %(ANNOT_KEY, name)] = value
        return property(get, set)

    exampleintprop = _getproperty("exampleintprop", default = 0)

    exampletextprop = _getproperty("exampletextprop", default = u"")


class TestWebDAVRequest(WebDAVRequest):
    """."""
    def __init__(self, elem = None):
        if elem is not None:
            body = """<?xml version="1.0" encoding="utf-8" ?>
<D:propertyupdate xmlns:D="DAV:">
  <D:set>
    <D:prop />
  </D:set>
</D:propertyupdate>
"""
            f = StringIO(body)
        else:
            f = StringIO('')

        super(TestWebDAVRequest, self).__init__(
            f, {'CONTENT_TYPE': 'text/xml',
                'CONTENT_LENGTH': len(f.getvalue()),
                })

        # processInputs to test request
        self.processInputs()

        # if elem is given insert it into the proppatch request.
        if elem is not None:
            self.xmlDataSource[0][0].append(elem)


class EmptyCollectionResource(Folder):
    """This collection doesn't contain any subitems
    """
    pass


def EmptyWriteDirectory(context):
    return None

class ICollectionResource(zope.app.folder.interfaces.IFolder):

    title = schema.TextLine(
        title = u"Title",
        description = u"Title of resource")


class CollectionResource(Folder):
    interface.implements(ICollectionResource)

    title = None


class IResource(interface.Interface):
    """ """

    title = schema.TextLine(
        title = u"Title",
        description = u"Title of resource")

    content = schema.Bytes(
        title = u"Content",
        description = u"Content of the resource")

class Resource(persistent.Persistent):
    interface.implements(IResource)

    title = None

    content = None


class DisplayNameStorageAdapter(object):
    interface.implements(zope.webdav.coreproperties.IDAVDisplayname)

    def __init__(self, context, request):
        self.context = context

    @apply
    def displayname():
        def get(self):
            return self.context.title
        def set(self, value):
            self.context.title = value
        return property(get, set)


class GETContentLength(object):
    component.adapts(IResource, zope.webdav.interfaces.IWebDAVRequest)
    interface.implements(zope.webdav.coreproperties.IDAVGetcontentlength)

    def __init__(self, context, request):
        self.context = context

    @property
    def getcontentlength(self):
        return len(self.context.content)


class DeadProperties(object):
    interface.implements(zope.webdav.interfaces.IOpaquePropertyStorage)

    def __init__(self, context):
        self.context = context
        # This is only a test so aren't that concerned with security at this
        # point.
        self.annots = getattr(removeSecurityProxy(self.context), "annots", None)

    def getAllProperties(self):
        if self.annots is not None:
            for tag in self.annots:
                yield tag

    def hasProperty(self, tag):
        if self.annots is not None and tag in self.annots:
            return True
        return False

    def getProperty(self, tag):
        if self.annots is not None:
            return self.annots.get(tag, None)
        return None

    def setProperty(self, tag, value):
        if self.annots is None:
            self.annots = removeSecurityProxy(self.context).annots = OOBTree()
        self.annots[tag] = value

    def removeProperty(self, tag):
        del self.annots[tag]


class DAVTestCase(HTTPTestCase):

    def setUp(self):
        super(DAVTestCase, self).setUp()

        gsm = component.getGlobalSiteManager()

        gsm.registerUtility(exampleIntProperty,
                            name = "{DAVtest:}exampleintprop",
                            provided = zope.webdav.interfaces.IDAVProperty)
        gsm.registerUtility(exampleTextProperty,
                            name = "{DAVtest:}exampletextprop",
                            provided = zope.webdav.interfaces.IDAVProperty)
        # this is to test the include and restricted allprop PROPFIND tests.
        exampleTextProperty.restricted = False

        gsm.registerAdapter(DisplayNameStorageAdapter,
                            (IResource, zope.webdav.interfaces.IWebDAVRequest))
        gsm.registerAdapter(DisplayNameStorageAdapter,
                            (ICollectionResource,
                             zope.webdav.interfaces.IWebDAVRequest))
        gsm.registerAdapter(GETContentLength)

        gsm.registerAdapter(DeadProperties, (IResource,))
        gsm.registerAdapter(DeadProperties, (ICollectionResource,))

        gsm.registerAdapter(ExamplePropertyStorage,
                            (IResource, zope.webdav.interfaces.IWebDAVRequest),
                            provided = IExamplePropertyStorage)

    def tearDown(self):
        gsm = component.getGlobalSiteManager()

        gsm.unregisterUtility(exampleIntProperty,
                              name = "{DAVtest:}exampleintprop",
                              provided = zope.webdav.interfaces.IDAVProperty)
        gsm.unregisterUtility(exampleTextProperty,
                              name = "{DAVtest:}exampletextprop",
                              provided = zope.webdav.interfaces.IDAVProperty)

        gsm.unregisterAdapter(DisplayNameStorageAdapter,
                            (IResource, zope.webdav.interfaces.IWebDAVRequest))
        gsm.unregisterAdapter(DisplayNameStorageAdapter,
                              (ICollectionResource,
                               zope.webdav.interfaces.IWebDAVRequest))
        gsm.unregisterAdapter(GETContentLength)

        gsm.unregisterAdapter(DeadProperties, (IResource,))
        gsm.unregisterAdapter(DeadProperties, (ICollectionResource,))

        gsm.unregisterAdapter(ExamplePropertyStorage,
                              (IResource,
                               zope.webdav.interfaces.IWebDAVRequest),
                              provided = IExamplePropertyStorage)

        super(DAVTestCase, self).tearDown()

        # logout just to make sure.
        self.logout()

    def login(self, principalid = "mgr"):
        """Some locking methods new an interaction in order to lock a resource
        """
        principal = Principal(principalid)
        participation = Participation(principal)
        newInteraction(participation)

    def logout(self):
        """End the current interaction so we run the publish method.
        """
        endInteraction()

    #
    # Some methods for creating dummy content.
    #
    def createCollections(self, path):
        collection = self.getRootFolder()
        if path[0] == '/':
            path = path[1:]
        path = path.split('/')
        for id in path[:-1]:
            try:
                collection = collection[id]
            except KeyError:
                collection[id] = CollectionResource()
                collection = collection[id]
        return collection, path[-1]

    def createObject(self, path, obj):
        collection, id = self.createCollections(path)
        collection[id] = obj
        transaction.commit()
        return collection[id]

    def addResource(self, path, content, title = None):
        resource = Resource()
        resource.content = content
        resource.title = title
        return self.createObject(path, resource)

    def addCollection(self, path, title = None):
        coll = CollectionResource()
        coll.title = title
        return self.createObject(path, coll)

    def addFile(self, path, content, contentType):
        resource = File(content, contentType)
        return self.createObject(path, resource)

    def createCollectionResourceStructure(self):
        """  _____ rootFolder/ _____
            /          \            \
           r1       __ a/ __          b/
                   /        \
                   r2       r3
        """
        self.addResource("/r1", "first resource")
        self.addResource("/a/r2", "second resource")
        self.addResource("/a/r3", "third resource")
        self.addCollection("/b")

    def createFolderFileStructure(self):
        """  _____ rootFolder/ _____
            /          \            \
           r1       __ a/ __          b/
                   /        \
                   r2       r3
        """
        self.addFile("/r1", "first resource", "test/plain")
        self.addFile("/a/r2", "second resource", "text/plain")
        self.addFile("/a/r3", "third resource", "text/plain")
        self.createObject("/b", Folder())

    #
    # Now some methods for creating, and publishing request.
    #
    def makeRequest(self, path = "", basic = None, form = None, env = {},
                    instream = None):
        """Create a new WebDAV request
        """
        if instream is None:
            instream = ""
        environment = {"HTTP_HOST": "localhost",
                       "HTTP_REFERER": "localhost"}
        environment.update(env)

        if instream and not environment.has_key("CONTENT_LENGTH"):
            if getattr(instream, "getvalue", None) is not None:
                instream = instream.getvalue()
            environment["CONTENT_LENGTH"] = len(instream)

        app = FunctionalTestSetup().getApplication()
        request = app._request(path, instream, environment = environment,
                               basic = basic, form = form,
                               request = WebDAVRequest,
                               publication = HTTPPublication)
        return request

    def checkPropfind(self, path = "/", basic = None, env = {},
                      properties = None):
        # - properties if set is a string containing the contents of the
        #   propfind XML element has specified in the WebDAV spec.
        if properties is not None:
            body = """<?xml version="1.0" encoding="utf-8" ?>
<propfind xmlns:D="DAV:" xmlns="DAV:">
  %s
</propfind>
""" % properties
            if not env.has_key("CONTENT_TYPE"):
                env["CONTENT_TYPE"] = "application/xml"
            env["CONTENT_LENGTH"] = len(body)
        else:
            body = ""
            env["CONTENT_LENGTH"] = 0

        if not env.has_key("REQUEST_METHOD"):
            env["REQUEST_METHOD"] = "PROPFIND"

        response = self.publish(path, basic = basic, env = env,
                                request_body = body)

        self.assertEqual(response.getStatus(), 207)
        self.assertEqual(response.getHeader("content-type"), "application/xml")

        respbody = response.getBody()
        etree = component.getUtility(IEtree)
        xmlbody = etree.fromstring(respbody)

        return response, xmlbody

    def checkProppatch(self, path = '/', basic = None, env = {},
                       set_properties = None, remove_properties = None,
                       handle_errors = True):
        # - set_properties is None or a string that is the XML fragment
        #   that should be included within the <D:set><D:prop> section of
        #   a PROPPATCH request.
        # - remove_properties is None or a string that is the XML fragment
        #   that should be included within the <D:remove><D:prop> section of
        #   a PROPPATCH request.
        set_body = ""
        if set_properties:
            set_body = "<D:set><D:prop>%s</D:prop></D:set>" % set_properties

        remove_body = ""
        if remove_properties:
            remove_body = "<D:remove><D:prop>%s</D:prop></D:remove>" % \
                          remove_properties

        body = """<?xml version="1.0" encoding="utf-8" ?>
<D:propertyupdate xmlns:D="DAV:" xmlns="DAV:">
  %s %s
</D:propertyupdate>
        """ %(set_body, remove_body)
        body = body.encode("utf-8")

        if not env.has_key("CONTENT_TYPE"):
            env["CONTENT_TYPE"] = "application/xml"
        env["CONTENT_LENGTH"] = len(body)

        if not env.has_key("REQUEST_METHOD"):
            env["REQUEST_METHOD"] = "PROPPATCH"

        response = self.publish(path, basic = basic, env = env,
                                request_body = body,
                                handle_errors = handle_errors)

        self.assertEqual(response.getStatus(), 207)
        self.assertEqual(response.getHeader("content-type"), "application/xml")

        respbody = response.getBody()
        etree = component.getUtility(IEtree)
        xmlbody = etree.fromstring(respbody)

        return response, xmlbody

    def assertMSPropertyValue(self, response, proptag, status = 200,
                              tag = None, text_value = None,
                              prop_element = None):
        # For the XML response element make sure that the proptag belongs
        # to the propstat element that has the given status.
        #   - response - etree XML element
        #   - proptag - tag name of the property we are testing
        #   - status - integre status code
        #   - tag - 
        #   - text_value -
        #   - propelement - etree Element that we compare with the property
        #                   using zope.webdav.testing.assertXMLEqual
        self.assertEqual(response.tag, "{DAV:}response")

        # set to true if we found the property, under the correct status code
        found_property = False

        propstats = response.findall("{DAV:}propstat")
        for propstat in propstats:
            statusresp = propstat.findall("{DAV:}status")
            self.assertEqual(len(statusresp), 1)

            if statusresp[0].text == "HTTP/1.1 %d %s" %(
                status, status_reasons[status]):
                # make sure that proptag is in this propstat element
                props = propstat.findall("{DAV:}prop/%s" % proptag)
                self.assertEqual(len(props), 1)
                prop = props[0]

                # now test the the tag and text match this propstat element
                if tag is not None:
                    ## XXX - this is not right.
                    ## self.assertEqual(len(prop), 1)
                    self.assertEqual(prop[0].tag, tag)
                else:
                    self.assertEqual(len(prop), 0)
                self.assertEqual(prop.text, text_value)

                if prop_element is not None:
                    assertXMLEqual(prop, prop_element)

                found_property = True
            else:
                # make sure that proptag is NOT in this propstat element
                props = propstat.findall("{DAV:}prop/%s" % proptag)
                self.assertEqual(len(props), 0)

        self.assert_(
            found_property,
            "The property %s doesn't exist for the status code %d" %(proptag,
                                                                     status))
