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

from zope import interface
from zope import component
from zope import schema
import zope.schema.interfaces
from zope.traversing.browser.interfaces import IAbsoluteURL

import zope.webdav.proppatch
import zope.webdav.publisher
import zope.webdav.interfaces
from zope.etree.interfaces import IEtree
from zope.etree.testing import etreeSetup, etreeTearDown, assertXMLEqual

class TestRequest(zope.webdav.publisher.WebDAVRequest):

    def __init__(self, set_properties = None, remove_properties = None,
                 environ = {}):
        set_body = ""
        if set_properties is not None:
            set_body = "<set><prop>%s</prop></set>" % set_properties

        remove_body = ""
        if remove_properties is not None:
            remove_body = "<remove><prop>%s</prop></remove>" % remove_properties

        body = """<?xml version="1.0" encoding="utf-8" ?>
<D:propertyupdate xmlns:D="DAV:" xmlns="DAV:">
  %s %s
</D:propertyupdate>
        """ %(set_body, remove_body)
        body = body.encode("utf-8")

        env = environ.copy()
        env.setdefault("REQUEST_METHOD", "PROPPATCH")
        env.setdefault("CONTENT_TYPE", "text/xml")
        env.setdefault("CONTENT_LENGTH", len(body))

        super(TestRequest, self).__init__(StringIO(body), env)

        # call processInputs now since we are in a unit test.
        self.processInputs()


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
##         elif ICollection.providedBy(self.context):
##             path += "/collection"
        else:
            raise ValueError("unknown context type")

        return path

    __call__ = __str__


class PROPPATCHHandler(zope.webdav.proppatch.PROPPATCH):

    def __init__(self, context, request):
        super(PROPPATCHHandler, self).__init__(context, request)

        self.setprops = []
        self.removeprops = []

    def handleSet(self, prop):
        self.setprops.append(prop.tag)

    def handleRemove(self, prop):
        self.removeprops.append(prop.tag)


class PROPPATCHXmlParsing(unittest.TestCase):

    def setUp(self):
        etreeSetup()

        gsm = component.getGlobalSiteManager()

        gsm.registerAdapter(DummyResourceURL,
                            (IResource, zope.webdav.interfaces.IWebDAVRequest))

    def tearDown(self):
        etreeTearDown()

        gsm = component.getGlobalSiteManager()

        gsm.unregisterAdapter(DummyResourceURL,
                              (IResource,
                               zope.webdav.interfaces.IWebDAVRequest))

    def test_noxml(self):
        request = zope.webdav.publisher.WebDAVRequest(StringIO(""), {})
        propp = PROPPATCHHandler(Resource(), request)
        self.assertRaises(zope.webdav.interfaces.BadRequest, propp.PROPPATCH)

    def test_notxml(self):
        request = zope.webdav.publisher.WebDAVRequest(
            StringIO("content"), {"CONTENT_TYPE": "text/plain",
                                  "CONTENT_LENGTH": 7})
        propp = PROPPATCHHandler(Resource(), request)
        request.processInputs()
        self.assertRaises(zope.webdav.interfaces.BadRequest, propp.PROPPATCH)

    def test_notproppatch(self):
        body = """<?xml version="1.0" encoding="utf-8" ?>
<D:notpropertyupdate xmlns:D="DAV:" xmlns="DAV:">
  Not a propertyupdate element.
</D:notpropertyupdate>
        """

        request = zope.webdav.publisher.WebDAVRequest(
            StringIO(body), {"CONTENT_TYPE": "text/xml",
                             "CONTENT_LENGTH": len(body)})
        request.processInputs()

        propp = PROPPATCHHandler(Resource(), request)
        self.assertRaises(zope.webdav.interfaces.UnprocessableError,
                          propp.PROPPATCH)

    def test_not_set_element(self):
        body = """<?xml version="1.0" encoding="utf-8" ?>
<propertyupdate xmlns:D="DAV:" xmlns="DAV:">
  <notset><prop><displayname>Display name</displayname></prop></notset>
</propertyupdate>
        """

        request = zope.webdav.publisher.WebDAVRequest(
            StringIO(body), {"CONTENT_TYPE": "text/xml",
                             "CONTENT_LENGTH": len(body)})
        request.processInputs()

        propp = PROPPATCHHandler(Resource(), request)
        propp.PROPPATCH()

        self.assertEqual(propp.setprops, [])
        self.assertEqual(propp.removeprops, [])

    def test_not_prop_element(self):
        body = """<?xml version="1.0" encoding="utf-8" ?>
<propertyupdate xmlns:D="DAV:" xmlns="DAV:">
  <set><notprop><displayname>Display name</displayname></notprop></set>
</propertyupdate>
        """

        request = zope.webdav.publisher.WebDAVRequest(
            StringIO(body), {"CONTENT_TYPE": "text/xml",
                             "CONTENT_LENGTH": len(body)})
        request.processInputs()

        propp = PROPPATCHHandler(Resource(), request)
        propp.PROPPATCH()

        self.assertEqual(propp.setprops, [])
        self.assertEqual(propp.removeprops, [])

    def test_not_remove_element(self):
        body = """<?xml version="1.0" encoding="utf-8" ?>
<propertyupdate xmlns:D="DAV:" xmlns="DAV:">
  <notremove><prop><displayname>Display name</displayname></prop></notremove>
</propertyupdate>
        """

        request = zope.webdav.publisher.WebDAVRequest(
            StringIO(body), {"CONTENT_TYPE": "text/xml",
                             "CONTENT_LENGTH": len(body)})
        request.processInputs()

        propp = PROPPATCHHandler(Resource(), request)
        propp.PROPPATCH()

        self.assertEqual(propp.setprops, [])
        self.assertEqual(propp.removeprops, [])

    def test_set_none_prop(self):
        request = TestRequest()
        propp = PROPPATCHHandler(Resource(), request)
        propp.PROPPATCH()

        self.assertEqual(propp.setprops, [])
        self.assertEqual(propp.removeprops, [])

    def test_set_one_prop(self):
        request = TestRequest(
            set_properties = "<displayname>Display name</displayname>")
        propp = PROPPATCHHandler(Resource(), request)
        propp.PROPPATCH()

        self.assertEqual(propp.setprops, ["{DAV:}displayname"])
        self.assertEqual(propp.removeprops, [])

    def test_remove_one_prop(self):
        request = TestRequest(
            remove_properties = "<displayname>Display name</displayname>")
        propp = PROPPATCHHandler(Resource(), request)
        propp.PROPPATCH()

        self.assertEqual(propp.setprops, [])
        self.assertEqual(propp.removeprops, ["{DAV:}displayname"])

    def test_multiset(self):
        request = TestRequest(
            set_properties = "<displayname>Display name</displayname><getcontenttype>text/plain</getcontenttype>")
        propp = PROPPATCHHandler(Resource(), request)
        propp.PROPPATCH()

        self.assertEqual(propp.setprops, ["{DAV:}displayname",
                                          "{DAV:}getcontenttype"])
        self.assertEqual(propp.removeprops, [])

    def test_multiremove(self):
        request = TestRequest(
            remove_properties = "<displayname>Display name</displayname><getcontenttype>text/plain</getcontenttype>")
        propp = PROPPATCHHandler(Resource(), request)
        propp.PROPPATCH()

        self.assertEqual(propp.setprops, [])
        self.assertEqual(propp.removeprops, ["{DAV:}displayname",
                                             "{DAV:}getcontenttype"])

    def test_set_remove_prop(self):
        request = TestRequest(
            remove_properties = "<displayname>Display name</displayname>",
            set_properties = "<getcontenttype>text/plain</getcontenttype>")
        propp = PROPPATCHHandler(Resource(), request)
        propp.PROPPATCH()

        self.assertEqual(propp.setprops, ["{DAV:}getcontenttype"])
        self.assertEqual(propp.removeprops, ["{DAV:}displayname"])

    def test_error_set_prop(self):
        class PROPPATCHHandlerError(PROPPATCHHandler):
            def handleSet(self, prop):
                raise zope.webdav.interfaces.PropertyNotFound(
                    self.context, "getcontenttype", u"property is missing")

        request = TestRequest(
            set_properties = "<getcontenttype>text/plain</getcontenttype>")
        propp = PROPPATCHHandlerError(Resource(), request)
        self.assertRaises(zope.webdav.interfaces.WebDAVPropstatErrors,
                          propp.PROPPATCH)

        self.assertEqual(propp.setprops, [])
        self.assertEqual(propp.removeprops, [])

    def test_error_set_prop_with_remove(self):
        class PROPPATCHHandlerError(PROPPATCHHandler):
            def handleSet(self, prop):
                raise zope.webdav.interfaces.PropertyNotFound(
                    self.context, "getcontenttype", u"property is missing")

        request = TestRequest(
            remove_properties = "<displayname>Test Name</displayname>",
            set_properties = "<getcontenttype>text/plain</getcontenttype>")
        propp = PROPPATCHHandlerError(Resource(), request)
        self.assertRaises(zope.webdav.interfaces.WebDAVPropstatErrors,
                          propp.PROPPATCH)

        self.assertEqual(propp.setprops, [])
        self.assertEqual(propp.removeprops, ['{DAV:}displayname'])

    def test_response(self):
        request = TestRequest(
            remove_properties = "<displayname>Display name</displayname>",
            set_properties = "<getcontenttype>text/plain</getcontenttype>")
        propp = PROPPATCHHandler(Resource(), request)
        result = propp.PROPPATCH()

        assertXMLEqual(result, """<ns0:multistatus xmlns:ns0="DAV:">
<ns0:response xmlns:ns0="DAV:">
  <ns0:href xmlns:ns0="DAV:">/resource</ns0:href>
  <ns0:propstat xmlns:ns0="DAV:">
    <ns0:prop xmlns:ns0="DAV:">
      <ns0:getcontenttype xmlns:ns0="DAV:"/>
      <ns0:displayname xmlns:ns0="DAV:"/>
    </ns0:prop>
    <ns0:status xmlns:ns0="DAV:">HTTP/1.1 200 OK</ns0:status>
  </ns0:propstat>
</ns0:response></ns0:multistatus>""")


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


class PROPPATCHHandlePropertyModification(unittest.TestCase):

    def setUp(self):
        etreeSetup()

        gsm = component.getGlobalSiteManager()

        gsm.registerUtility(exampleIntProperty,
                            name = "{DAVtest:}exampleintprop",
                            provided = zope.webdav.interfaces.IDAVProperty)
        gsm.registerUtility(exampleTextProperty,
                            name = "{DAVtest:}exampletextprop",
                            provided = zope.webdav.interfaces.IDAVProperty)
        exampleTextProperty.field.readonly = False
        gsm.registerUtility(extraTextProperty,
                            name = "{DAVtest:}extratextprop",
                            provided = zope.webdav.interfaces.IDAVProperty)

        gsm.registerAdapter(ExamplePropertyStorage,
                            (IResource, zope.webdav.interfaces.IWebDAVRequest),
                            provided = IExamplePropertyStorage)

        gsm.registerAdapter(zope.webdav.widgets.TextDAVInputWidget,
                            (zope.schema.interfaces.IText,
                             zope.webdav.interfaces.IWebDAVRequest))

    def tearDown(self):
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

        gsm.unregisterAdapter(ExamplePropertyStorage,
                              (IResource,
                               zope.webdav.interfaces.IWebDAVRequest),
                              provided = IExamplePropertyStorage)

        gsm.unregisterAdapter(zope.webdav.widgets.TextDAVInputWidget,
                              (zope.schema.interfaces.IText,
                               zope.webdav.interfaces.IWebDAVRequest))

    def test_handleSetProperty(self):
        etree = component.getUtility(IEtree)
        propel = etree.Element("{DAVtest:}exampletextprop")
        propel.text = "Example Text Prop"

        request = TestRequest(
            set_properties = """<Dt:exampletextprop xmlns:Dt="DAVtest:">Example Text Prop</Dt:exampletextprop>""")
        resource = Resource("Text Prop", 10)

        propp = zope.webdav.proppatch.PROPPATCH(resource, request)
        propp.handleSet(propel)

        self.assertEqual(resource.text, "Example Text Prop")

    def test_handleSet_forbidden_property(self):
        etree = component.getUtility(IEtree)
        propel = etree.Element("{DAVtest:}exampletextprop")
        propel.text = "Example Text Prop"

        exampleTextProperty.field.readonly = True

        request = TestRequest(
            set_properties = """<Dt:exampletextprop xmlns:Dt="DAVtest:">Example Text Prop</Dt:exampletextprop>""")
        resource = Resource("Text Prop", 10)

        propp = zope.webdav.proppatch.PROPPATCH(resource, request)
        self.assertRaises(zope.webdav.interfaces.ForbiddenError,
                          propp.handleSet,
                          propel)

    def test_handleSet_property_notfound(self):
        etree = component.getUtility(IEtree)
        propel = etree.Element("{DAVtest:}exampletextpropmissing")
        propel.text = "Example Text Prop"

        request = TestRequest(
            set_properties = """<Dt:exampletextprop xmlns:Dt="DAVtest:">Example Text Prop</Dt:exampletextprop>""")
        resource = Resource("Text Prop", 10)

        propp = zope.webdav.proppatch.PROPPATCH(resource, request)
        self.assertRaises(zope.webdav.interfaces.PropertyNotFound,
                          propp.handleSet,
                          propel)

    def test_handleRemove_live_property(self):
        etree = component.getUtility(IEtree)
        propel = etree.Element("{DAVtest:}exampletextprop")
        propel.text = "Example Text Prop"

        request = TestRequest(
            remove_properties = """<Dt:exampletextprop xmlns:Dt="DAVtest:">Example Text Prop</Dt:exampletextprop>""")
        resource = Resource("Text Prop", 10)

        propp = zope.webdav.proppatch.PROPPATCH(resource, request)
        self.assertRaises(zope.webdav.interfaces.ConflictError,
                          propp.handleRemove,
                          propel)

    def test_handleRemove_no_dead_properties(self):
        etree = component.getUtility(IEtree)
        propel = etree.Element("{example:}exampledeadprop")
        propel.text = "Example Text Prop"

        request = TestRequest(
            remove_properties = """<Dt:exampletextprop xmlns:Dt="DAVtest:">Example Text Prop</Dt:exampletextprop>""")
        resource = Resource("Text Prop", 10)

        propp = zope.webdav.proppatch.PROPPATCH(resource, request)
        self.assertRaises(zope.webdav.interfaces.ConflictError,
                          propp.handleRemove,
                          propel)


class DEADProperties(object):
    interface.implements(zope.webdav.interfaces.IOpaquePropertyStorage)

    def __init__(self, context):
        self.data = context.props = getattr(context, "props", {})

    def getAllProperties(self):
        for tag in self.data:
            yield tag

    def hasProperty(self, tag):
        return tag in self.data

    def getProperty(self, tag):
        return self.data[tag]

    def setProperty(self, tag, value):
        self.data[tag] = value

    def removeProperty(self, tag):
        del self.data[tag]


class PROPPATCHHandlePropertyRemoveDead(unittest.TestCase):

    def setUp(self):
        etreeSetup()

        gsm = component.getGlobalSiteManager()

        gsm.registerAdapter(DEADProperties, (IResource,))

    def tearDown(self):
        etreeTearDown()

        gsm = component.getGlobalSiteManager()

        gsm.unregisterAdapter(DEADProperties, (IResource,))

    def test_remove_no_storage(self):
        etree = component.getUtility(IEtree)
        propel = etree.Element("{example:}exampledeadprop")
        propel.text = "Example Text Prop"

        request = TestRequest(
            remove_properties = """<Dt:exampledeadprop xmlns:Dt="example:">Example Text Prop</Dt:exampledeadprop>""")
        resource = Resource("Text Prop", 10)

        propp = zope.webdav.proppatch.PROPPATCH(resource, request)
        self.assertRaises(zope.webdav.interfaces.ConflictError,
                          propp.handleRemove,
                          propel)

    def test_remove_not_there(self):
        etree = component.getUtility(IEtree)
        propel = etree.Element("{example:}exampledeadprop")
        propel.text = "Example Text Prop"

        request = TestRequest(
            remove_properties = """<Dt:exampletextprop xmlns:Dt="DAVtest:">Example Text Prop</Dt:exampletextprop>""")
        resource = Resource("Text Prop", 10)

        propp = zope.webdav.proppatch.PROPPATCH(resource, request)
        self.assertRaises(zope.webdav.interfaces.ConflictError,
                          propp.handleRemove,
                          propel)

    def test_remove_prop(self):
        etree = component.getUtility(IEtree)
        propel = etree.Element("{example:}exampledeadprop")
        propel.text = "Example Text Prop"

        request = TestRequest(
            remove_properties = """<Dt:exampletextprop xmlns:Dt="DAVtest:">Example Text Prop</Dt:exampletextprop>""")
        resource = Resource("Text Prop", 10)

        testprop = "{example:}exampledeadprop"

        deadprops = DEADProperties(resource)
        deadprops.setProperty(testprop, "Example Text Prop")
        self.assertEqual(deadprops.hasProperty(testprop), True)
        self.assertEqual(deadprops.getProperty(testprop), "Example Text Prop")

        propp = zope.webdav.proppatch.PROPPATCH(resource, request)

        propp.handleRemove(propel)

        self.assertEqual(deadprops.hasProperty(testprop), False)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(PROPPATCHXmlParsing),
        unittest.makeSuite(PROPPATCHHandlePropertyModification),
        unittest.makeSuite(PROPPATCHHandlePropertyRemoveDead),
        ))
