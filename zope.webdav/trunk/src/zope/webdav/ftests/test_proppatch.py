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
"""Collection of functional tests for PROPFIND zope.webdav

$Id$
"""

import unittest
from cStringIO import StringIO
import transaction

from zope import component

import dav

import zope.webdav.interfaces
from zope.webdav.publisher import WebDAVRequest
from zope.etree.testing import assertXMLEqual

class PROPPATCHTestCase(dav.DAVTestCase):

    def test_badcontent(self):
        response = self.publish("/", env = {"REQUEST_METHOD": "PROPPATCH"},
                                request_body = "some content",
                                handle_errors = True)
        self.assertEqual(response.getStatus(), 400)
        self.assert_(
            "All PROPPATCH requests needs a XML body" in response.getBody())

    def test_invalidxml(self):
        body = """<?xml version="1.0" encoding="utf-8" ?>
<D:propfind xmlns:D="DAV:">
  <D:prop />
</D:propfind>
        """
        response = self.publish("/", env = {"REQUEST_METHOD": "PROPPATCH",
                                            "CONTENT_TYPE": "application/xml",
                                            "CONTENT_LENGTH": len(body)},
                                request_body = body,
                                handle_errors = True)

        self.assertEqual(response.getStatus(), 422)
        self.assertEqual(response.getBody(), "")

    def test_setdisplayname(self):
        set_properties = "<D:displayname>Test File</D:displayname>"
        file = self.addResource("/r", "some content", "Test Resource")

        self.assertEqual(self.getRootFolder()["r"].title, "Test Resource")

        httpresponse, xmlbody = self.checkProppatch(
            "/r", basic = "mgr:mgrpw", set_properties = set_properties)

        responses = xmlbody.findall("{DAV:}response")
        self.assertEqual(len(responses), 1)
        response = responses[0]

        self.assertMSPropertyValue(response, "{DAV:}displayname")

        self.assertEqual(self.getRootFolder()["r"].title, u"Test File")

    def test_readonly_property(self):
        set_properties = "<D:getcontentlength>10</D:getcontentlength>"
        file = self.addResource("/r", "some file content", "Test Resource")

        httpresponse, xmlbody = self.checkProppatch(
            "/r", basic = "mgr:mgrpw", set_properties = set_properties)

        responses = xmlbody.findall("{DAV:}response")
        self.assertEqual(len(responses), 1)
        response = responses[0]
        hrefs = response.findall("{DAV:}href")
        self.assertEqual(len(hrefs), 1)
        self.assertEqual(hrefs[0].text, "http://localhost/r")

        self.assertMSPropertyValue(response, "{DAV:}getcontentlength",
                                   status = 403)

##     def test_property_notfound(self):
##         set_properties = """
##         <E:notfound xmlns:E="example:">Not Existent Prop</E:notfound>
##         """
##         file = self.addFile("/testfile", "some file content", "text/plain")

##         httpresponse, xmlbody = self.checkProppatch(
##             "/testfile", basic = "mgr:mgrpw", set_properties = set_properties)

##         responses = xmlbody.findall("{DAV:}response")
##         self.assertEqual(len(responses), 1)
##         response = responses[0]
##         hrefs = response.findall("{DAV:}href")
##         self.assertEqual(len(hrefs), 1)
##         self.assertEqual(hrefs[0].text, "http://localhost/testfile")

##         self.assertMSPropertyValue(response, "{example:}notfound",
##                                    status = 404)

    def test_badinput(self):
        set_properties = """
        <E:exampleintprop xmlns:E="DAVtest:">BAD INT</E:exampleintprop>
        """
        resource = self.addResource("/testresource", "some resource content")

        httpresponse, xmlbody = self.checkProppatch(
            "/testresource", basic = "mgr:mgrpw",
            set_properties = set_properties)

        responses = xmlbody.findall("{DAV:}response")
        self.assertEqual(len(responses), 1)
        response = responses[0]
        hrefs = response.findall("{DAV:}href")
        self.assertEqual(len(hrefs), 1)
        self.assertEqual(hrefs[0].text, "http://localhost/testresource")

        self.assertMSPropertyValue(response, "{DAVtest:}exampleintprop",
                                   status = 409)

    def test_badinput_plus_faileddep(self):
        set_properties = """
        <E:exampleintprop xmlns:E="DAVtest:">BAD INT</E:exampleintprop>
        <E:exampletextprop xmlns:E="DAVtest:">
          Test Property
        </E:exampletextprop>
        """
        resource = self.addResource("/testresource", "some resource content")

        request = WebDAVRequest(StringIO(""), {})
        exampleStorage = component.getMultiAdapter((resource, request),
                                                   dav.IExamplePropertyStorage)
        # set up a default value to test later
        exampleStorage.exampletextprop = u"Example Text Property"
        transaction.commit()

        httpresponse, xmlbody = self.checkProppatch(
            "/testresource", basic = "mgr:mgrpw",
            set_properties = set_properties)

        responses = xmlbody.findall("{DAV:}response")
        self.assertEqual(len(responses), 1)
        response = responses[0]
        hrefs = response.findall("{DAV:}href")
        self.assertEqual(len(hrefs), 1)
        self.assertEqual(hrefs[0].text, "http://localhost/testresource")

        self.assertMSPropertyValue(response, "{DAVtest:}exampletextprop",
                                   status = 424)
        self.assertMSPropertyValue(response, "{DAVtest:}exampleintprop",
                                   409)

        exampleStorage = component.getMultiAdapter((resource, request),
                                                   dav.IExamplePropertyStorage)
        self.assertEqual(exampleStorage.exampletextprop,
                         u"Example Text Property")

    def test_proppatch_opaqueproperty(self):
        set_properties = """<Z:Author xmlns:Z="http://ns.example.com/z39.50/">
Jim Whitehead
</Z:Author>
        """
        file = self.addResource("/r", "some content", "Test Resource")

        httpresponse, xmlbody = self.checkProppatch(
            "/r", basic = "mgr:mgrpw", set_properties = set_properties)

        opaqueProperties = zope.webdav.interfaces.IOpaquePropertyStorage(file)
        self.assertEqual(opaqueProperties.hasProperty(
            "{http://ns.example.com/z39.50/}Author"), True)
        assertXMLEqual(opaqueProperties.getProperty(
            "{http://ns.example.com/z39.50/}Author"),
            """<Z:Author xmlns:Z="http://ns.example.com/z39.50/">
Jim Whitehead
</Z:Author>""")

    def test_set_multiple_dead_props(self):
        set_properties = """<E:prop0 xmlns:E="example:">PROP0</E:prop0>
<E:prop1 xmlns:E="example:">PROP0</E:prop1>
<E:prop2 xmlns:E="example:">PROP0</E:prop2>
<E:prop3 xmlns:E="example:">PROP0</E:prop3>
        """

        file = self.addResource("/r", "some content", "Test Resource")

        httpresponse, xmlbody = self.checkProppatch(
            "/r", basic = "mgr:mgrpw", set_properties = set_properties)

        opaqueProperties = zope.webdav.interfaces.IOpaquePropertyStorage(file)
        allprops = [tag for tag in opaqueProperties.getAllProperties()]
        allprops.sort()
        self.assertEqual(allprops, ["{example:}prop0", "{example:}prop1",
                                    "{example:}prop2", "{example:}prop3"])

    def test_unicode_title(self):
        teststr = u"copyright \xa9 me"
        set_properties = "<D:displayname>%s</D:displayname>" % teststr
        file = self.addResource("/r", "some content", "Test Resource")

        self.assertEqual(file.title, "Test Resource")

        httpresponse, xmlbody = self.checkProppatch(
            "/r", basic = "mgr:mgrpw", set_properties = set_properties)

        responses = xmlbody.findall("{DAV:}response")
        self.assertEqual(len(responses), 1)
        response = responses[0]

        self.assertMSPropertyValue(response, "{DAV:}displayname")

    def test_remove_live_prop(self):
        file = self.addResource("/r", "some content", "Test Resource")

        opaqueProperties = zope.webdav.interfaces.IOpaquePropertyStorage(file)
        opaqueProperties.setProperty("{deadprop:}deadprop",
                                     """<X:deadprop xmlns:X="deadprop:">
This is a dead property.</X:deadprop>""")
        transaction.commit()

        httpresponse, xmlbody = self.checkProppatch(
            "/r", basic = "mgr:mgrpw",
            remove_properties = """<E:exampleintprop xmlns:E="DAVtest:" />""")

        responses = xmlbody.findall("{DAV:}response")
        self.assertEqual(len(responses), 1)
        response = responses[0]

        hrefs = response.findall("{DAV:}href")
        self.assertEqual(len(hrefs), 1)
        self.assertEqual(hrefs[0].text, "http://localhost/r")

        propstat = response.findall("{DAV:}propstat")
        self.assertEqual(len(propstat), 1)
        propstat = propstat[0]

        self.assertEqual(len(propstat), 2)

        props = propstat.findall("{DAV:}prop")
        self.assertEqual(len(props), 1)
        self.assertEqual(len(props[0]), 1) # there is only one property.

        self.assertMSPropertyValue(response, "{DAVtest:}exampleintprop",
                                   status = 409)

    def test_remove_dead_prop(self):
        proptag = "{deadprop:}deadprop"
        file = self.addResource("/r", "some content", "Test Resource")

        opaqueProperties = zope.webdav.interfaces.IOpaquePropertyStorage(file)
        opaqueProperties.setProperty(proptag,
                                     """<X:deadprop xmlns:X="deadprop:">
This is a dead property.</X:deadprop>""")
        transaction.commit()

        httpresponse, xmlbody = self.checkProppatch(
            "/r", basic = "mgr:mgrpw",
            remove_properties = """<X:deadprop xmlns:X="deadprop:" />""")

        responses = xmlbody.findall("{DAV:}response")
        self.assertEqual(len(responses), 1)
        response = responses[0]

        self.assertMSPropertyValue(response, proptag)

        opaqueProperties = zope.webdav.interfaces.IOpaquePropertyStorage(file)
        self.assertEqual(opaqueProperties.hasProperty(proptag), False)

    def test_setting_unicode_title(self):
        teststr = u"copyright \xa9 me"
        file = self.addResource(u"/" + teststr, "some file content",
                                title = "Old title")

        httpresponse, xmlbody = self.checkProppatch(
            "/" + teststr.encode("utf-8"), basic = "mgr:mgrpw",
            set_properties = "<D:displayname>%s</D:displayname>" % teststr)

        responses = xmlbody.findall("{DAV:}response")
        self.assertEqual(len(responses), 1)
        response = responses[0]

        self.assertMSPropertyValue(response, "{DAV:}displayname")
        resource = self.getRootFolder()[teststr]
        self.assertEqual(resource.title, teststr)


def test_suite():
    return unittest.TestSuite((
            unittest.makeSuite(PROPPATCHTestCase),
            ))

if __name__ == "__main__":
    unittest.main(defaultTest = "test_suite")
