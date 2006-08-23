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

It is easier to do this has a unit test has we have complete control over
what properties are defined or not.

$Id$
"""

import unittest
from cStringIO import StringIO
import UserDict

from zope import interface
from zope import component
from zope import schema
import zope.schema.interfaces
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.app.container.interfaces import IReadContainer

import zope.webdav.properties
import zope.webdav.publisher
import zope.webdav.widgets
import zope.webdav.exceptions
import zope.webdav.coreproperties
from zope.webdav.propfind import PROPFIND
from zope.webdav.testing import etreeSetup, etreeTearDown, assertXMLEqual

class TestRequest(zope.webdav.publisher.WebDAVRequest):

    def __init__(self, properties = None, environ = {}):
        if properties is not None:
            body = """<?xml version="1.0" encoding="utf-8" ?>
<propfind xmlns:D="DAV:" xmlns="DAV:">
  %s
</propfind>
""" % properties
        else:
            body = ""

        env = environ.copy()
        env.setdefault("REQUEST_METHOD", "PROPFIND")
        env.setdefault("CONTENT_TYPE", "text/xml")
        env.setdefault("CONTENT_LENGTH", len(body))

        super(TestRequest, self).__init__(StringIO(body), env)

        # call processInputs now since we are in a unit test.
        self.processInputs()


class PROPFINDBodyParsed(PROPFIND):

    propertiesFactory = extraArg = depth = None

    def handlePropfindResource(self, ob, req,
                               depth, propertiesFactory, extraArg):
        self.propertiesFactory = propertiesFactory
        self.extraArg = extraArg
        self.depth = depth

        return []


class PROPFINDBodyTestCase(unittest.TestCase):
    # Using PROPFINDBodyParsed test that the correct method and arguements
    # get set up.

    def setUp(self):
        etreeSetup()

    def tearDown(self):
        etreeTearDown()

    def checkPropfind(self, properties = None, environ = {}):
        request = TestRequest(properties = properties, environ = environ)
        propfind = PROPFINDBodyParsed(None, request)
        propfind.PROPFIND()

        return propfind

    def test_notxml(self):
        self.assertRaises(zope.webdav.interfaces.BadRequest, self.checkPropfind,
            "<propname />", {"CONTENT_TYPE": "text/plain"})

    def test_bad_depthheader(self):
        self.assertRaises(zope.webdav.interfaces.BadRequest, self.checkPropfind,
            "<propname />", {"DEPTH": "2"})

    def test_depth_header(self):
        propf = self.checkPropfind("<propname />", {"DEPTH": "0"})
        self.assertEqual(propf.depth, "0")
        propf = self.checkPropfind("<propname />", {"DEPTH": "1"})
        self.assertEqual(propf.depth, "1")
        propf = self.checkPropfind("<propname />", {"DEPTH": "infinity"})
        self.assertEqual(propf.depth, "infinity")

    def test_xml_propname(self):
        propf = self.checkPropfind("<propname />")
        self.assertEqual(propf.propertiesFactory, propf.renderPropnames)
        self.assertEqual(propf.extraArg, None)

    def test_xml_allprop(self):
        propf = self.checkPropfind("<allprop />")
        self.assertEqual(propf.propertiesFactory, propf.renderAllProperties)
        self.assertEqual(propf.extraArg, None)

    def test_xml_allprop_with_include(self):
        includes = """<include xmlns="DAV:"><davproperty /></include>"""
        propf = self.checkPropfind("<allprop/>%s" % includes)
        self.assertEqual(propf.propertiesFactory, propf.renderAllProperties)
        assertXMLEqual(propf.extraArg, includes)

    def test_xml_emptyprop(self):
        propf = self.checkPropfind("<prop />")
        self.assertEqual(propf.propertiesFactory, propf.renderAllProperties)
        self.assertEqual(propf.extraArg, None)

    def test_xml_someprops(self):
        props = """<prop xmlns="DAV:"><someprop/></prop>"""
        propf = self.checkPropfind(props)
        self.assertEqual(propf.propertiesFactory,
                         propf.renderSelectedProperties)
        assertXMLEqual(propf.extraArg, props)

    def test_emptybody(self):
        propf = self.checkPropfind()
        self.assertEqual(propf.propertiesFactory, propf.renderAllProperties)
        self.assertEqual(propf.extraArg, None)

    def test_xml_nopropfind_element(self):
        body = """<?xml version="1.0" encoding="utf-8" ?>
<nopropfind xmlns:D="DAV:" xmlns="DAV:">
  invalid xml
</nopropfind>
        """
        env = {"CONTENT_TYPE": "text/xml",
               "CONTENT_LENGTH": len(body)}
        request = zope.webdav.publisher.WebDAVRequest(StringIO(body), env)
        request.processInputs()

        propf = PROPFINDBodyParsed(None, request)
        self.assertRaises(zope.webdav.interfaces.UnprocessableError,
                          propf.PROPFIND)

    def test_xml_propfind_bad_content(self):
        self.assertRaises(zope.webdav.interfaces.UnprocessableError,
                          self.checkPropfind, properties = "<noproperties />")


class IExamplePropertyStorage(interface.Interface):

    exampleintprop = schema.Int(
        title = u"Example Integer Property")

    exampletextprop = schema.Text(
        title = u"Example Text Property")

class IExtraPropertyStorage(interface.Interface):

    extratextprop = schema.Text(
        title = u"Property with no storage")

exampleIntProperty = zope.webdav.properties.DAVProperty(
    "{DAVtest:}exampleintprop", IExamplePropertyStorage)
exampleTextProperty = zope.webdav.properties.DAVProperty(
    "{DAVtest:}exampletextprop", IExamplePropertyStorage)
extraTextProperty = zope.webdav.properties.DAVProperty(
    "{DAVtest:}extratextprop", IExtraPropertyStorage)

class ExamplePropertyStorage(object):
    interface.implements(IExamplePropertyStorage)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _getproperty(name, default = None):
        def get(self):
            return getattr(self.context, name, default)
        def set(self, value):
            setattr(self.context, name, value)
        return property(get, set)

    exampleintprop = _getproperty("intprop", default = 0)

    exampletextprop = _getproperty("text", default = u"")


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


class ICollection(IReadContainer):
    pass


class Collection(UserDict.UserDict):
    interface.implements(ICollection)

    def __setitem__(self, key, value):
        self.data[key] = value
        value.__parent__ = self
        value.__name__ = key


class DummyResourceURL(object):
    interface.implements(IAbsoluteURL)

    def __init__(self, context, request):
        self.context = context

    def __str__(self):
        if getattr(self.context, "__parent__", None) is not None:
            path = DummyResourceURL(self.context.__parent__, None)()
        else:
            path = ""

        if getattr(self.context, "__name__", None) is not None:
            path += "/" + self.context.__name__
        elif IResource.providedBy(self.context):
            path += "/resource"
        elif ICollection.providedBy(self.context):
            path += "/collection"
        else:
            raise ValueError("unknown context type")

        return path

    __call__ = __str__


def propfindSetUp():
    etreeSetup()

    gsm = component.getGlobalSiteManager()

    gsm.registerUtility(exampleIntProperty,
                        name = "{DAVtest:}exampleintprop",
                        provided = zope.webdav.interfaces.IDAVProperty)
    gsm.registerUtility(exampleTextProperty,
                        name = "{DAVtest:}exampletextprop",
                        provided = zope.webdav.interfaces.IDAVProperty)
    exampleTextProperty.restricted = False
    gsm.registerUtility(extraTextProperty,
                        name = "{DAVtest:}extratextprop",
                        provided = zope.webdav.interfaces.IDAVProperty)
    gsm.registerUtility(zope.webdav.coreproperties.resourcetype,
                        name = "{DAV:}resourcetype")

    gsm.registerAdapter(ExamplePropertyStorage,
                        (IResource, zope.webdav.interfaces.IWebDAVRequest),
                        provided = IExamplePropertyStorage)
    gsm.registerAdapter(zope.webdav.coreproperties.ResourceTypeAdapter)

    gsm.registerAdapter(DummyResourceURL,
                        (IResource, zope.webdav.interfaces.IWebDAVRequest))
    gsm.registerAdapter(DummyResourceURL,
                        (ICollection, zope.webdav.interfaces.IWebDAVRequest))

    gsm.registerAdapter(zope.webdav.widgets.TextDAVWidget,
                        (zope.schema.interfaces.IText,
                         zope.webdav.interfaces.IWebDAVRequest))
    gsm.registerAdapter(zope.webdav.widgets.IntDAVWidget,
                        (zope.schema.interfaces.IInt,
                         zope.webdav.interfaces.IWebDAVRequest))
    gsm.registerAdapter(zope.webdav.widgets.ListDAVWidget,
                        (zope.schema.interfaces.IList,
                         zope.webdav.interfaces.IWebDAVRequest))

    gsm.registerAdapter(zope.webdav.exceptions.PropertyNotFoundError,
                        (zope.webdav.interfaces.IPropertyNotFound,
                         zope.webdav.interfaces.IWebDAVRequest))

def propfindTearDown():
    etreeTearDown()

    gsm = component.getGlobalSiteManager()

    gsm.unregisterUtility(exampleIntProperty,
                          name = "{DAVtest:}exampleintprop",
                          provided = zope.webdav.interfaces.IDAVProperty)
    gsm.unregisterUtility(exampleTextProperty,
                          name = "{DAVtest:}exampletextprop",
                          provided = zope.webdav.interfaces.IDAVProperty)
    gsm.unregisterUtility(extraTextProperty,
                          name = "{DAVtest:}extratextprop",
                          provided = zope.webdav.interfaces.IDAVProperty)
    gsm.unregisterUtility(zope.webdav.coreproperties.resourcetype,
                          name = "{DAV:}resourcetype")

    gsm.unregisterAdapter(ExamplePropertyStorage,
                          (IResource, zope.webdav.interfaces.IWebDAVRequest),
                          provided = IExamplePropertyStorage)
    gsm.unregisterAdapter(zope.webdav.coreproperties.ResourceTypeAdapter)

    gsm.unregisterAdapter(DummyResourceURL,
                          (IResource, zope.webdav.interfaces.IWebDAVRequest))
    gsm.unregisterAdapter(DummyResourceURL,
                          (ICollection, zope.webdav.interfaces.IWebDAVRequest))

    gsm.unregisterAdapter(zope.webdav.widgets.TextDAVWidget,
                          (zope.schema.interfaces.IText,
                           zope.webdav.interfaces.IWebDAVRequest))
    gsm.unregisterAdapter(zope.webdav.widgets.IntDAVWidget,
                          (zope.schema.interfaces.IInt,
                           zope.webdav.interfaces.IWebDAVRequest))
    gsm.unregisterAdapter(zope.webdav.exceptions.PropertyNotFoundError,
                          (zope.webdav.interfaces.IPropertyNotFound,
                           zope.webdav.interfaces.IWebDAVRequest))
    gsm.unregisterAdapter(zope.webdav.widgets.ListDAVWidget,
                          (zope.schema.interfaces.IList,
                           zope.webdav.interfaces.IWebDAVRequest))


class PROPFINDTestRender(unittest.TestCase):
    # Test all the methods that render a resource into a `response' XML
    # element. We are going to need to register the DAV widgets for
    # text and int properties.

    def setUp(self):
        propfindSetUp()

    def tearDown(self):
        propfindTearDown()

    def test_renderPropnames(self):
        resource = Resource("some text", 10)
        request = zope.webdav.publisher.WebDAVRequest(StringIO(""), {})

        propf = PROPFIND(None, None)
        response = propf.renderPropnames(resource, request, None)
        assertXMLEqual(response(), """<ns0:response xmlns:ns0="DAV:">
<ns0:href xmlns:ns0="DAV:">/resource</ns0:href>
<ns0:propstat xmlns:ns0="DAV:" xmlns:ns01="DAVtest:">
  <ns0:prop xmlns:ns0="DAV:">
    <ns01:exampletextprop xmlns:ns0="DAVtest:"/>
    <ns01:exampleintprop xmlns:ns0="DAVtest:"/>
    <ns0:resourcetype />
  </ns0:prop>
  <ns0:status xmlns:ns0="DAV:">HTTP/1.1 200 OK</ns0:status>
</ns0:propstat></ns0:response>""")

    def test_renderSelected(self):
        resource = Resource("some text", 10)
        request = zope.webdav.publisher.WebDAVRequest(StringIO(""), {})
        propf = PROPFIND(None, None)

        etree = component.getUtility(zope.webdav.ietree.IEtree)
        props = etree.fromstring("""<prop xmlns="DAV:" xmlns:D="DAVtest:">
<D:exampletextprop />
<D:exampleintprop />
</prop>""")
        response = propf.renderSelectedProperties(resource, request, props)

        assertXMLEqual(response(), """<ns0:response xmlns:ns0="DAV:">
<ns0:href xmlns:ns0="DAV:">/resource</ns0:href>
<ns0:propstat xmlns:ns0="DAV:" xmlns:ns01="DAVtest:">
  <ns0:prop xmlns:ns0="DAV:">
    <ns01:exampletextprop xmlns:ns0="DAVtest:">some text</ns01:exampletextprop>
    <ns01:exampleintprop xmlns:ns0="DAVtest:">10</ns01:exampleintprop>
  </ns0:prop>
  <ns0:status xmlns:ns0="DAV:">HTTP/1.1 200 OK</ns0:status>
</ns0:propstat></ns0:response>""")

    def test_renderSelected_notfound(self):
        resource = Resource("some text", 10)
        request = zope.webdav.publisher.WebDAVRequest(StringIO(""), {})
        propf = PROPFIND(None, None)

        etree = component.getUtility(zope.webdav.ietree.IEtree)
        props = etree.fromstring("""<prop xmlns="DAV:" xmlns:D="DAVtest:">
<D:exampletextprop />
<D:extratextprop />
</prop>""")
        response = propf.renderSelectedProperties(resource, request, props)

        assertXMLEqual(response(), """<ns0:response xmlns:ns0="DAV:">
<ns0:href xmlns:ns0="DAV:">/resource</ns0:href>
<ns0:propstat xmlns:ns0="DAV:" xmlns:ns01="DAVtest:">
  <ns0:prop xmlns:ns0="DAV:">
    <ns01:exampletextprop xmlns:ns0="DAVtest:">some text</ns01:exampletextprop>
  </ns0:prop>
  <ns0:status xmlns:ns0="DAV:">HTTP/1.1 200 OK</ns0:status>
</ns0:propstat>
<ns0:propstat xmlns:ns0="DAV:" xmlns:ns01="DAVtest:">
  <ns0:prop xmlns:ns0="DAV:">
    <ns01:extratextprop xmlns:ns0="DAVtest:" />
  </ns0:prop>
  <ns0:status xmlns:ns0="DAV:">HTTP/1.1 404 Not Found</ns0:status>
</ns0:propstat>
</ns0:response>""")

    def test_renderAllProperties(self):
        resource = Resource("some text", 10)
        request = zope.webdav.publisher.WebDAVRequest(StringIO(""), {})
        propf = PROPFIND(None, None)

        response = propf.renderAllProperties(resource, request, None)

        assertXMLEqual(response(), """<ns0:response xmlns:ns0="DAV:">
<ns0:href xmlns:ns0="DAV:">/resource</ns0:href>
<ns0:propstat xmlns:ns0="DAV:" xmlns:ns01="DAVtest:">
  <ns0:prop xmlns:ns0="DAV:">
    <ns01:exampletextprop xmlns:ns0="DAVtest:">some text</ns01:exampletextprop>
    <ns01:exampleintprop xmlns:ns0="DAVtest:">10</ns01:exampleintprop>
    <ns0:resourcetype />
  </ns0:prop>
  <ns0:status xmlns:ns0="DAV:">HTTP/1.1 200 OK</ns0:status>
</ns0:propstat></ns0:response>""")

    def test_renderAllProperties_withInclude(self):
        resource = Resource("some text", 10)
        request = zope.webdav.publisher.WebDAVRequest(StringIO(""), {})
        propf = PROPFIND(None, None)

        etree = component.getUtility(zope.webdav.ietree.IEtree)
        include = etree.fromstring("""<include xmlns="DAV:" xmlns:D="DAVtest:">
<D:exampletextprop />
</include>""")
        response = propf.renderAllProperties(resource, request, include)

        assertXMLEqual(response(), """<ns0:response xmlns:ns0="DAV:">
<ns0:href xmlns:ns0="DAV:">/resource</ns0:href>
<ns0:propstat xmlns:ns0="DAV:" xmlns:ns01="DAVtest:">
  <ns0:prop xmlns:ns0="DAV:">
    <ns01:exampletextprop xmlns:ns0="DAVtest:">some text</ns01:exampletextprop>
    <ns01:exampleintprop xmlns:ns0="DAVtest:">10</ns01:exampleintprop>
    <ns0:resourcetype />
  </ns0:prop>
  <ns0:status xmlns:ns0="DAV:">HTTP/1.1 200 OK</ns0:status>
</ns0:propstat></ns0:response>""")

    def test_renderAllProperties_withRestrictedProp(self):
        resource = Resource("some text", 10)
        request = zope.webdav.publisher.WebDAVRequest(StringIO(""), {})
        propf = PROPFIND(None, None)

        exampleTextProperty.restricted = True
        response = propf.renderAllProperties(resource, request, None)

        assertXMLEqual(response(), """<ns0:response xmlns:ns0="DAV:">
<ns0:href xmlns:ns0="DAV:">/resource</ns0:href>
<ns0:propstat xmlns:ns0="DAV:" xmlns:ns01="DAVtest:">
  <ns0:prop xmlns:ns0="DAV:">
    <ns01:exampleintprop xmlns:ns0="DAVtest:">10</ns01:exampleintprop>
    <ns0:resourcetype />
  </ns0:prop>
  <ns0:status xmlns:ns0="DAV:">HTTP/1.1 200 OK</ns0:status>
</ns0:propstat></ns0:response>""")

    def test_renderAllProperties_withRestrictedProp_include(self):
        resource = Resource("some text", 10)
        request = zope.webdav.publisher.WebDAVRequest(StringIO(""), {})
        propf = PROPFIND(None, None)

        exampleTextProperty.restricted = True
        etree = component.getUtility(zope.webdav.ietree.IEtree)
        include = etree.fromstring("""<include xmlns="DAV:" xmlns:D="DAVtest:">
<D:exampletextprop />
</include>""")
        response = propf.renderAllProperties(resource, request, include)

        assertXMLEqual(response(), """<ns0:response xmlns:ns0="DAV:">
<ns0:href xmlns:ns0="DAV:">/resource</ns0:href>
<ns0:propstat xmlns:ns0="DAV:" xmlns:ns01="DAVtest:">
  <ns0:prop xmlns:ns0="DAV:">
    <ns01:exampletextprop xmlns:ns0="DAVtest:">some text</ns01:exampletextprop>
    <ns01:exampleintprop xmlns:ns0="DAVtest:">10</ns01:exampleintprop>
    <ns0:resourcetype />
  </ns0:prop>
  <ns0:status xmlns:ns0="DAV:">HTTP/1.1 200 OK</ns0:status>
</ns0:propstat></ns0:response>""")


class PROPFINDRecuseTest(unittest.TestCase):

    def setUp(self):
        propfindSetUp()

    def tearDown(self):
        propfindTearDown()

    def test_handlePropfindResource(self):
        collection = Collection()
        collection["r1"] = Resource("some text - r1", 2)
        collection["c"] = Collection()
        collection["c"]["r2"] = Resource("some text - r2", 4)
        request = zope.webdav.publisher.WebDAVRequest(StringIO(""), {})
        request.processInputs()
        propf = PROPFIND(collection, request)

        result = propf.PROPFIND()
        etree = component.getUtility(zope.webdav.ietree.IEtree)
        etree.fromstring(result)

        assertXMLEqual(result, """<ns0:multistatus xmlns:ns0="DAV:">
<ns0:response xmlns:ns0="DAV:">
  <ns0:href xmlns:ns0="DAV:">/collection/</ns0:href>
  <ns0:propstat xmlns:ns0="DAV:">
    <ns0:prop xmlns:ns0="DAV:">
      <ns0:resourcetype xmlns:ns0="DAV:"><ns0:collection xmlns:ns0="DAV:"/></ns0:resourcetype>
    </ns0:prop>
    <ns0:status xmlns:ns0="DAV:">HTTP/1.1 200 OK</ns0:status>
  </ns0:propstat>
</ns0:response>
<ns0:response xmlns:ns0="DAV:">
  <ns0:href xmlns:ns0="DAV:">/collection/c/</ns0:href>
  <ns0:propstat xmlns:ns0="DAV:">
    <ns0:prop xmlns:ns0="DAV:">
      <ns0:resourcetype xmlns:ns0="DAV:"><ns0:collection xmlns:ns0="DAV:"/></ns0:resourcetype>
    </ns0:prop>
    <ns0:status xmlns:ns0="DAV:">HTTP/1.1 200 OK</ns0:status>
  </ns0:propstat>
</ns0:response>
<ns0:response xmlns:ns0="DAV:" xmlns:ns01="DAVtest:">
  <ns0:href xmlns:ns0="DAV:">/collection/c/r2</ns0:href>
  <ns0:propstat xmlns:ns0="DAV:" xmlns:ns01="DAVtest:">
    <ns0:prop xmlns:ns0="DAV:">
      <ns01:exampletextprop xmlns:ns0="DAVtest:">some text - r2</ns01:exampletextprop>
      <ns01:exampleintprop xmlns:ns0="DAVtest:">4</ns01:exampleintprop>
      <ns0:resourcetype xmlns:ns0="DAV:"/>
    </ns0:prop>
    <ns0:status xmlns:ns0="DAV:">HTTP/1.1 200 OK</ns0:status>
  </ns0:propstat>
</ns0:response>
<ns0:response xmlns:ns0="DAV:" xmlns:ns01="DAVtest:">
  <ns0:href xmlns:ns0="DAV:">/collection/r1</ns0:href>
  <ns0:propstat xmlns:ns0="DAV:" xmlns:ns01="DAVtest:">
    <ns0:prop xmlns:ns0="DAV:">
      <ns01:exampletextprop xmlns:ns0="DAVtest:">some text - r1</ns01:exampletextprop>
      <ns01:exampleintprop xmlns:ns0="DAVtest:">2</ns01:exampleintprop>
      <ns0:resourcetype xmlns:ns0="DAV:"/>
    </ns0:prop>
    <ns0:status xmlns:ns0="DAV:">HTTP/1.1 200 OK</ns0:status>
  </ns0:propstat>
</ns0:response></ns0:multistatus>
        """)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(PROPFINDBodyTestCase),
        unittest.makeSuite(PROPFINDTestRender),
        unittest.makeSuite(PROPFINDRecuseTest),
        ))
