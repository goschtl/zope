##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""WebDAV ``PROPFIND`` HTTP verb implementation

$Id$
"""
__docformat__ = 'restructuredtext'
from StringIO import StringIO
from unittest import TestCase, TestSuite, main, makeSuite
from datetime import datetime

from zope.interface import implements, directlyProvides
from zope.component import getView
from zope.publisher.interfaces.http import IHTTPRequest
from zope.pagetemplate.tests.util import normalize_xml
from zope.schema import getFieldNamesInOrder
from zope.schema.interfaces import IText, ITextLine, IDatetime, ISequence

from zope.app import zapi
from zope.app.tests import ztapi

from zope.app.traversing.api import traverse
from zope.publisher.browser import TestRequest
from zope.app.filerepresentation.interfaces import IWriteFile
from zope.app.site.tests.placefulsetup import PlacefulSetup
from zope.app.traversing.browser import AbsoluteURL
from zope.app.container.interfaces import IReadContainer
from zope.app.dublincore.interfaces import IZopeDublinCore
from zope.app.dublincore.annotatableadapter import ZDCAnnotatableAdapter
from zope.app.annotation.interfaces import IAnnotatable, IAnnotations
from zope.app.annotation.attribute import AttributeAnnotations

from zope.app.dav import propfind
from zope.app.dav.interfaces import IDAVSchema
from zope.app.dav.interfaces import IDAVNamespace
from zope.app.dav.interfaces import IDAVWidget
from zope.app.dav.widget import TextDAVWidget, SequenceDAVWidget

import zope.app.location

class Folder(zope.app.location.Location):

    implements(IReadContainer)

    def __init__(self, name, level=0, parent=None):
        self.name = self.__name__ = name
        self.level=level
        self.__parent__ = parent

    def items(self):
        if self.level == 2:
            return (('last', File('last', 'text/plain', 'blablabla', self)),)
        result = []
        for i in range(1, 3):
            result.append((str(i),
                           File(str(i), 'text/plain', 'blablabla', self)))
        result.append(('sub1',
                       Folder('sub1', level=self.level+1, parent=self)))
        return tuple(result)

class File(zope.app.location.Location):

    implements(IWriteFile)

    def __init__(self, name, content_type, data, parent=None):
        self.name = self.__name__ = name
        self.content_type = content_type
        self.data = data
        self.__parent__ = parent

    def write(self, data):
        self.data = data

class FooZPT(zope.app.location.Location):

    implements(IAnnotatable)

    def getSource(self):
        return 'bla bla bla'


def _createRequest(body=None, headers=None, skip_headers=None):
    if body is None:
        body = '''<?xml version="1.0"  ?>

        <propfind xmlns="DAV:">
        <prop xmlns:R="http://www.foo.bar/boxschema/">
        <R:bigbox/>
        <R:author/>
        <R:DingALing/>
        <R:Random/>
        </prop>
        </propfind>
        '''

    _environ = {'CONTENT_TYPE': 'text/xml',
                'CONTENT_LENGTH': str(len(body))}

    if headers is not None:
        for key, value in headers.items():
            _environ[key.upper().replace("-", "_")] = value

    if skip_headers is not None:
        for key in skip_headers:
            if _environ.has_key(key.upper()):
                del _environ[key.upper()]

    request = TestRequest(StringIO(body), StringIO(), _environ)
    return request

class TestPlacefulPROPFIND(PlacefulSetup, TestCase):

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
        ps = zapi.getGlobalService(zapi.servicenames.Presentation)
        ps.provideView(None, 'absolute_url', IHTTPRequest,
                       AbsoluteURL)
        ps.provideView(None, 'PROPFIND', IHTTPRequest,
                       propfind.PROPFIND)
        ztapi.browserViewProviding(IText, TextDAVWidget, IDAVWidget)
        ztapi.browserViewProviding(ITextLine, TextDAVWidget, IDAVWidget)
        ztapi.browserViewProviding(IDatetime, TextDAVWidget, IDAVWidget)
        ztapi.browserViewProviding(ISequence, SequenceDAVWidget, IDAVWidget)
        ztapi.provideAdapter(IAnnotatable, IAnnotations, AttributeAnnotations)
        ztapi.provideAdapter(IAnnotatable, IZopeDublinCore,
                             ZDCAnnotatableAdapter)
        utils = zapi.getGlobalService('Utilities')
        directlyProvides(IDAVSchema, IDAVNamespace)
        utils.provideUtility(IDAVNamespace, IDAVSchema, 'DAV:')
        directlyProvides(IZopeDublinCore, IDAVNamespace)
        utils.provideUtility(IDAVNamespace, IZopeDublinCore,
                             'http://www.purl.org/dc/1.1')

    def test_contenttype1(self):
        file = self.file
        request = _createRequest(headers={'Content-type':'text/xml'})
        pfind = propfind.PROPFIND(file, request)
        pfind.PROPFIND()
        # Check HTTP Response
        self.assertEqual(request.response.getStatus(), 207)

    def test_contenttype2(self):
        file = self.file
        request = _createRequest(headers={'Content-type':'application/xml'})

        pfind = propfind.PROPFIND(file, request)
        pfind.PROPFIND()
        # Check HTTP Response
        self.assertEqual(request.response.getStatus(), 207)

    def test_contenttype3(self):
        # Check for an appropriate response when the content-type has
        # parameters, and that the major/minor parts are treated in a
        # case-insensitive way.
        file = self.file
        request = _createRequest(headers={'Content-type':
                                          'TEXT/XML; charset="utf-8"'})
        pfind = propfind.PROPFIND(file, request)
        pfind.PROPFIND()
        # Check HTTP Response
        self.assertEqual(request.response.getStatus(), 207)

    def test_bad_contenttype(self):
        file = self.file
        request = _createRequest(headers={'Content-type':'text/foo'})

        pfind = propfind.PROPFIND(file, request)
        pfind.PROPFIND()
        # Check HTTP Response
        self.assertEqual(request.response.getStatus(), 400)

    def test_no_contenttype(self):
        file = self.file
        request = _createRequest(skip_headers=('content-type'))

        pfind = propfind.PROPFIND(file, request)
        pfind.PROPFIND()
        # Check HTTP Response
        self.assertEqual(request.response.getStatus(), 207)
        self.assertEqual(pfind.content_type, 'text/xml')

    def test_nodepth(self):
        file = self.file
        request = _createRequest(headers={'Content-type':'text/xml'})

        pfind = propfind.PROPFIND(file, request)
        pfind.PROPFIND()
        # Check HTTP Response
        self.assertEqual(request.response.getStatus(), 207)
        self.assertEqual(pfind.getDepth(), 'infinity')

    def test_depth0(self):
        file = self.file
        request = _createRequest(headers={'Content-type':'text/xml',
                                               'Depth':'0'})

        pfind = propfind.PROPFIND(file, request)
        pfind.PROPFIND()
        # Check HTTP Response
        self.assertEqual(request.response.getStatus(), 207)
        self.assertEqual(pfind.getDepth(), '0')

    def test_depth1(self):
        file = self.file
        request = _createRequest(headers={'Content-type':'text/xml',
                                               'Depth':'1'})

        pfind = propfind.PROPFIND(file, request)
        pfind.PROPFIND()
        # Check HTTP Response
        self.assertEqual(request.response.getStatus(), 207)
        self.assertEqual(pfind.getDepth(), '1')

    def test_depthinf(self):
        file = self.file
        request = _createRequest(headers={'Content-type':'text/xml',
                                               'Depth':'infinity'})

        pfind = propfind.PROPFIND(file, request)
        pfind.PROPFIND()
        # Check HTTP Response
        self.assertEqual(request.response.getStatus(), 207)
        self.assertEqual(pfind.getDepth(), 'infinity')

    def test_depthinvalid(self):
        file = self.file
        request = _createRequest(headers={'Content-type':'text/xml',
                                               'Depth':'full'})

        pfind = propfind.PROPFIND(file, request)
        pfind.PROPFIND()
        # Check HTTP Response
        self.assertEqual(request.response.getStatus(), 400)
        self.assertEqual(pfind.getDepth(), 'full')

    def test_davpropdctitle(self):
        root = self.rootFolder
        zpt = traverse(root, 'zpt')
        dc = IZopeDublinCore(zpt)
        dc.title = u'Test Title'
        body = '''<?xml version="1.0" ?>
        <propfind xmlns="DAV:">
        <prop xmlns:DC="http://www.purl.org/dc/1.1">
        <DC:title />
        </prop>
        </propfind>
        '''

        request = _createRequest(body=body,
                                 headers={'Content-type':'text/xml',
                                          'Depth':'0'})

        resource_url = str(getView(zpt, 'absolute_url', request))
        expect = '''<?xml version="1.0" ?>
        <multistatus xmlns="DAV:">
        <response>
        <href>%(resource_url)s</href>
        <propstat>
        <prop xmlns:a0="http://www.purl.org/dc/1.1">
        <title xmlns="a0">Test Title</title>
        </prop>
        <status>HTTP/1.1 200 OK</status>
        </propstat>
        </response>
        </multistatus>
        ''' % {'resource_url':resource_url}

        pfind = propfind.PROPFIND(zpt, request)
        pfind.PROPFIND()
        # Check HTTP Response
        self.assertEqual(request.response.getStatus(), 207)
        self.assertEqual(pfind.getDepth(), '0')
        s1 = normalize_xml(request.response._body)
        s2 = normalize_xml(expect)
        self.assertEqual(s1, s2)

    def test_davpropdccreated(self):
        root = self.rootFolder
        zpt = traverse(root, 'zpt')
        dc = IZopeDublinCore(zpt)
        dc.created = datetime.utcnow()
        body = '''<?xml version="1.0" ?>
        <propfind xmlns="DAV:">
        <prop xmlns:DC="http://www.purl.org/dc/1.1">
        <DC:created />
        </prop>
        </propfind>
        '''

        request = _createRequest(body=body,
                                 headers={'Content-type':'text/xml',
                                          'Depth':'0'})

        resource_url = str(getView(zpt, 'absolute_url', request))
        expect = '''<?xml version="1.0" ?>
        <multistatus xmlns="DAV:">
        <response>
        <href>%(resource_url)s</href>
        <propstat>
        <prop xmlns:a0="http://www.purl.org/dc/1.1">
        <created xmlns="a0">%(created)s</created>
        </prop>
        <status>HTTP/1.1 200 OK</status>
        </propstat>
        </response>
        </multistatus>
        ''' % {'resource_url':resource_url,
               'created': dc.created }

        pfind = propfind.PROPFIND(zpt, request)
        pfind.PROPFIND()
        # Check HTTP Response
        self.assertEqual(request.response.getStatus(), 207)
        self.assertEqual(pfind.getDepth(), '0')
        s1 = normalize_xml(request.response._body)
        s2 = normalize_xml(expect)
        self.assertEqual(s1, s2)

    def test_davpropdcsubjects(self):
        root = self.rootFolder
        zpt = traverse(root, 'zpt')
        dc = IZopeDublinCore(zpt)
        dc.subjects = (u'Bla', u'Ble', u'Bli')
        body = '''<?xml version="1.0" ?>
        <propfind xmlns="DAV:">
        <prop xmlns:DC="http://www.purl.org/dc/1.1">
        <DC:subjects />
        </prop>
        </propfind>
        '''

        request = _createRequest(body=body,
                                 headers={'Content-type':'text/xml',
                                          'Depth':'0'})

        resource_url = str(getView(zpt, 'absolute_url', request))
        expect = '''<?xml version="1.0" ?>
        <multistatus xmlns="DAV:">
        <response>
        <href>%(resource_url)s</href>
        <propstat>
        <prop xmlns:a0="http://www.purl.org/dc/1.1">
        <subjects xmlns="a0">%(subjects)s</subjects>
        </prop>
        <status>HTTP/1.1 200 OK</status>
        </propstat>
        </response>
        </multistatus>
        ''' % {'resource_url':resource_url,
               'subjects': u', '.join(dc.subjects) }

        pfind = propfind.PROPFIND(zpt, request)
        pfind.PROPFIND()
        # Check HTTP Response
        self.assertEqual(request.response.getStatus(), 207)
        self.assertEqual(pfind.getDepth(), '0')
        s1 = normalize_xml(request.response._body)
        s2 = normalize_xml(expect)
        self.assertEqual(s1, s2)

    def test_davpropname(self):
        root = self.rootFolder
        zpt = traverse(root, 'zpt')
        body = '''<?xml version="1.0" ?>
        <propfind xmlns="DAV:">
        <propname/>
        </propfind>
        '''

        request = _createRequest(body=body,
                                 headers={'Content-type':'text/xml',
                                          'Depth':'0'})

        resource_url = str(getView(zpt, 'absolute_url', request))
        props_xml = ''
        props = getFieldNamesInOrder(IZopeDublinCore)
        for p in props:
            props_xml += '<%s xmlns="a0"/>' % p
        props = getFieldNamesInOrder(IDAVSchema)
        for p in props:
            props_xml += '<%s/>' % p
        expect = '''<?xml version="1.0" ?>
        <multistatus xmlns="DAV:">
        <response>
        <href>%(resource_url)s</href>
        <propstat>
        <prop xmlns:a0="http://www.purl.org/dc/1.1">
        %(props_xml)s
        </prop>
        <status>HTTP/1.1 200 OK</status>
        </propstat>
        </response>
        </multistatus>
        ''' % {'resource_url':resource_url,
               'props_xml':props_xml}

        pfind = propfind.PROPFIND(zpt, request)
        pfind.PROPFIND()
        # Check HTTP Response
        self.assertEqual(request.response.getStatus(), 207)
        self.assertEqual(pfind.getDepth(), '0')
        s1 = normalize_xml(request.response._body)
        s2 = normalize_xml(expect)
        self.assertEqual(s1, s2)

    def test_davpropnamefolderdepth0(self):
        root = self.rootFolder
        folder = traverse(root, 'folder')
        body = '''<?xml version="1.0" ?>
        <propfind xmlns="DAV:">
        <propname/>
        </propfind>
        '''

        request = _createRequest(body=body,
                                 headers={'Content-type':'text/xml',
                                          'Depth':'0'})

        resource_url = str(getView(folder, 'absolute_url', request))
        resource_url = "%s/" % resource_url
        props_xml = ''
        props = getFieldNamesInOrder(IZopeDublinCore)
        for p in props:
            props_xml += '<%s xmlns="a0"/>' % p
        props = getFieldNamesInOrder(IDAVSchema)
        for p in props:
            props_xml += '<%s/>' % p
        expect = '''<?xml version="1.0" ?>
        <multistatus xmlns="DAV:">
        <response>
        <href>%(resource_url)s</href>
        <propstat>
        <prop xmlns:a0="http://www.purl.org/dc/1.1">
        %(props_xml)s
        </prop>
        <status>HTTP/1.1 200 OK</status>
        </propstat>
        </response>
        </multistatus>
        ''' % {'resource_url':resource_url,
               'props_xml':props_xml}

        pfind = propfind.PROPFIND(folder, request)

        pfind.PROPFIND()
        # Check HTTP Response
        self.assertEqual(request.response.getStatus(), 207)
        self.assertEqual(pfind.getDepth(), '0')
        s1 = normalize_xml(request.response._body)
        s2 = normalize_xml(expect)
        self.assertEqual(s1, s2)

    def test_davpropnamefolderdepth1(self):
        root = self.rootFolder
        folder = traverse(root, 'folder')
        body = '''<?xml version="1.0" ?>
        <propfind xmlns="DAV:">
        <propname/>
        </propfind>
        '''

        request = _createRequest(body=body,
                                 headers={'Content-type':'text/xml',
                                          'Depth':'1'})

        resource_url = str(getView(folder, 'absolute_url', request))
        resource_url = "%s/" % resource_url
        props_xml = ''
        props = getFieldNamesInOrder(IZopeDublinCore)
        for p in props:
            props_xml += '<%s xmlns="a0"/>' % p
        props = getFieldNamesInOrder(IDAVSchema)
        for p in props:
            props_xml += '<%s/>' % p

        expect = '''<?xml version="1.0" ?>
        <multistatus xmlns="DAV:">
        <response>
        <href>http://127.0.0.1/folder/</href>
        <propstat>
        <prop xmlns:a0="http://www.purl.org/dc/1.1">
        <title xmlns="a0"/>
        <description xmlns="a0"/>
        <created xmlns="a0"/>
        <modified xmlns="a0"/>
        <effective xmlns="a0"/>
        <expires xmlns="a0"/>
        <creators xmlns="a0"/>
        <subjects xmlns="a0"/>
        <publisher xmlns="a0"/>
        <contributors xmlns="a0"/>
        <creationdate/>
        <displayname/>
        <source/>
        <getcontentlanguage/>
        <getcontentlength/>
        <getcontenttype/>
        <getetag/>
        <getlastmodified/>
        <resourcetype/>
        <lockdiscovery/>
        <supportedlock/>
        </prop>
        <status>HTTP/1.1 200 OK</status>
        </propstat>
        </response>
        <response>
        <href>http://127.0.0.1/folder/1</href>
        <propstat>
        <prop xmlns:a0="http://www.purl.org/dc/1.1">
        <title xmlns="a0"/>
        <description xmlns="a0"/>
        <created xmlns="a0"/>
        <modified xmlns="a0"/>
        <effective xmlns="a0"/>
        <expires xmlns="a0"/>
        <creators xmlns="a0"/>
        <subjects xmlns="a0"/>
        <publisher xmlns="a0"/>
        <contributors xmlns="a0"/>
        <creationdate/>
        <displayname/>
        <source/>
        <getcontentlanguage/>
        <getcontentlength/>
        <getcontenttype/>
        <getetag/>
        <getlastmodified/>
        <resourcetype/>
        <lockdiscovery/>
        <supportedlock/>
        </prop>
        <status>HTTP/1.1 200 OK</status>
        </propstat>
        </response>
        <response>
        <href>http://127.0.0.1/folder/2</href>
        <propstat>
        <prop xmlns:a0="http://www.purl.org/dc/1.1">
        <title xmlns="a0"/>
        <description xmlns="a0"/>
        <created xmlns="a0"/>
        <modified xmlns="a0"/>
        <effective xmlns="a0"/>
        <expires xmlns="a0"/>
        <creators xmlns="a0"/>
        <subjects xmlns="a0"/>
        <publisher xmlns="a0"/>
        <contributors xmlns="a0"/>
        <creationdate/>
        <displayname/>
        <source/>
        <getcontentlanguage/>
        <getcontentlength/>
        <getcontenttype/>
        <getetag/>
        <getlastmodified/>
        <resourcetype/>
        <lockdiscovery/>
        <supportedlock/>
        </prop>
        <status>HTTP/1.1 200 OK</status>
        </propstat>
        </response>
        <response>
        <href>http://127.0.0.1/folder/sub1/</href>
        <propstat>
        <prop xmlns:a0="http://www.purl.org/dc/1.1">
        <title xmlns="a0"/>
        <description xmlns="a0"/>
        <created xmlns="a0"/>
        <modified xmlns="a0"/>
        <effective xmlns="a0"/>
        <expires xmlns="a0"/>
        <creators xmlns="a0"/>
        <subjects xmlns="a0"/>
        <publisher xmlns="a0"/>
        <contributors xmlns="a0"/>
        <creationdate/>
        <displayname/>
        <source/>
        <getcontentlanguage/>
        <getcontentlength/>
        <getcontenttype/>
        <getetag/>
        <getlastmodified/>
        <resourcetype/>
        <lockdiscovery/>
        <supportedlock/>
        </prop>
        <status>HTTP/1.1 200 OK</status>
        </propstat>
        </response>
        </multistatus>'''


        pfind = propfind.PROPFIND(folder, request)

        pfind.PROPFIND()
        # Check HTTP Response
        self.assertEqual(request.response.getStatus(), 207)
        self.assertEqual(pfind.getDepth(), '1')
        s1 = normalize_xml(request.response._body)
        s2 = normalize_xml(expect)
        self.assertEqual(s1, s2)

    def test_davpropnamefolderdepthinfinity(self):
        root = self.rootFolder
        folder = traverse(root, 'folder')
        body = '''<?xml version="1.0" ?>
        <propfind xmlns="DAV:">
        <propname/>
        </propfind>
        '''

        request = _createRequest(body=body,
                                 headers={'Content-type':'text/xml',
                                          'Depth':'infinity'})

        resource_url = str(getView(folder, 'absolute_url', request))
        resource_url = "%s/" % resource_url
        props_xml = ''
        props = getFieldNamesInOrder(IZopeDublinCore)
        for p in props:
            props_xml += '<%s xmlns="a0"/>' % p
        props = getFieldNamesInOrder(IDAVSchema)
        for p in props:
            props_xml += '<%s/>' % p

        expect = '''<?xml version="1.0" ?>
        <multistatus xmlns="DAV:">
        <response>
        <href>http://127.0.0.1/folder/</href>
        <propstat>
        <prop xmlns:a0="http://www.purl.org/dc/1.1">
        <title xmlns="a0"/>
        <description xmlns="a0"/>
        <created xmlns="a0"/>
        <modified xmlns="a0"/>
        <effective xmlns="a0"/>
        <expires xmlns="a0"/>
        <creators xmlns="a0"/>
        <subjects xmlns="a0"/>
        <publisher xmlns="a0"/>
        <contributors xmlns="a0"/>
        <creationdate/>
        <displayname/>
        <source/>
        <getcontentlanguage/>
        <getcontentlength/>
        <getcontenttype/>
        <getetag/>
        <getlastmodified/>
        <resourcetype/>
        <lockdiscovery/>
        <supportedlock/>
        </prop>
        <status>HTTP/1.1 200 OK</status>
        </propstat>
        </response>
        <response>
        <href>http://127.0.0.1/folder/1</href>
        <propstat>
        <prop xmlns:a0="http://www.purl.org/dc/1.1">
        <title xmlns="a0"/>
        <description xmlns="a0"/>
        <created xmlns="a0"/>
        <modified xmlns="a0"/>
        <effective xmlns="a0"/>
        <expires xmlns="a0"/>
        <creators xmlns="a0"/>
        <subjects xmlns="a0"/>
        <publisher xmlns="a0"/>
        <contributors xmlns="a0"/>
        <creationdate/>
        <displayname/>
        <source/>
        <getcontentlanguage/>
        <getcontentlength/>
        <getcontenttype/>
        <getetag/>
        <getlastmodified/>
        <resourcetype/>
        <lockdiscovery/>
        <supportedlock/>
        </prop>
        <status>HTTP/1.1 200 OK</status>
        </propstat>
        </response>
        <response>
        <href>http://127.0.0.1/folder/2</href>
        <propstat>
        <prop xmlns:a0="http://www.purl.org/dc/1.1">
        <title xmlns="a0"/>
        <description xmlns="a0"/>
        <created xmlns="a0"/>
        <modified xmlns="a0"/>
        <effective xmlns="a0"/>
        <expires xmlns="a0"/>
        <creators xmlns="a0"/>
        <subjects xmlns="a0"/>
        <publisher xmlns="a0"/>
        <contributors xmlns="a0"/>
        <creationdate/>
        <displayname/>
        <source/>
        <getcontentlanguage/>
        <getcontentlength/>
        <getcontenttype/>
        <getetag/>
        <getlastmodified/>
        <resourcetype/>
        <lockdiscovery/>
        <supportedlock/>
        </prop>
        <status>HTTP/1.1 200 OK</status>
        </propstat>
        </response>
        <response>
        <href>http://127.0.0.1/folder/sub1/</href>
        <propstat>
        <prop xmlns:a0="http://www.purl.org/dc/1.1">
        <title xmlns="a0"/>
        <description xmlns="a0"/>
        <created xmlns="a0"/>
        <modified xmlns="a0"/>
        <effective xmlns="a0"/>
        <expires xmlns="a0"/>
        <creators xmlns="a0"/>
        <subjects xmlns="a0"/>
        <publisher xmlns="a0"/>
        <contributors xmlns="a0"/>
        <creationdate/>
        <displayname/>
        <source/>
        <getcontentlanguage/>
        <getcontentlength/>
        <getcontenttype/>
        <getetag/>
        <getlastmodified/>
        <resourcetype/>
        <lockdiscovery/>
        <supportedlock/>
        </prop>
        <status>HTTP/1.1 200 OK</status>
        </propstat>
        </response>
        <response>
        <href>http://127.0.0.1/folder/sub1/1</href>
        <propstat>
        <prop xmlns:a0="http://www.purl.org/dc/1.1">
        <title xmlns="a0"/>
        <description xmlns="a0"/>
        <created xmlns="a0"/>
        <modified xmlns="a0"/>
        <effective xmlns="a0"/>
        <expires xmlns="a0"/>
        <creators xmlns="a0"/>
        <subjects xmlns="a0"/>
        <publisher xmlns="a0"/>
        <contributors xmlns="a0"/>
        <creationdate/>
        <displayname/>
        <source/>
        <getcontentlanguage/>
        <getcontentlength/>
        <getcontenttype/>
        <getetag/>
        <getlastmodified/>
        <resourcetype/>
        <lockdiscovery/>
        <supportedlock/>
        </prop>
        <status>HTTP/1.1 200 OK</status>
        </propstat>
        </response>
        <response>
        <href>http://127.0.0.1/folder/sub1/2</href>
        <propstat>
        <prop xmlns:a0="http://www.purl.org/dc/1.1">
        <title xmlns="a0"/>
        <description xmlns="a0"/>
        <created xmlns="a0"/>
        <modified xmlns="a0"/>
        <effective xmlns="a0"/>
        <expires xmlns="a0"/>
        <creators xmlns="a0"/>
        <subjects xmlns="a0"/>
        <publisher xmlns="a0"/>
        <contributors xmlns="a0"/>
        <creationdate/>
        <displayname/>
        <source/>
        <getcontentlanguage/>
        <getcontentlength/>
        <getcontenttype/>
        <getetag/>
        <getlastmodified/>
        <resourcetype/>
        <lockdiscovery/>
        <supportedlock/>
        </prop>
        <status>HTTP/1.1 200 OK</status>
        </propstat>
        </response>
        <response>
        <href>http://127.0.0.1/folder/sub1/sub1/</href>
        <propstat>
        <prop xmlns:a0="http://www.purl.org/dc/1.1">
        <title xmlns="a0"/>
        <description xmlns="a0"/>
        <created xmlns="a0"/>
        <modified xmlns="a0"/>
        <effective xmlns="a0"/>
        <expires xmlns="a0"/>
        <creators xmlns="a0"/>
        <subjects xmlns="a0"/>
        <publisher xmlns="a0"/>
        <contributors xmlns="a0"/>
        <creationdate/>
        <displayname/>
        <source/>
        <getcontentlanguage/>
        <getcontentlength/>
        <getcontenttype/>
        <getetag/>
        <getlastmodified/>
        <resourcetype/>
        <lockdiscovery/>
        <supportedlock/>
        </prop>
        <status>HTTP/1.1 200 OK</status>
        </propstat>
        </response>
        <response>
        <href>http://127.0.0.1/folder/sub1/sub1/last</href>
        <propstat>
        <prop xmlns:a0="http://www.purl.org/dc/1.1">
        <title xmlns="a0"/>
        <description xmlns="a0"/>
        <created xmlns="a0"/>
        <modified xmlns="a0"/>
        <effective xmlns="a0"/>
        <expires xmlns="a0"/>
        <creators xmlns="a0"/>
        <subjects xmlns="a0"/>
        <publisher xmlns="a0"/>
        <contributors xmlns="a0"/>
        <creationdate/>
        <displayname/>
        <source/>
        <getcontentlanguage/>
        <getcontentlength/>
        <getcontenttype/>
        <getetag/>
        <getlastmodified/>
        <resourcetype/>
        <lockdiscovery/>
        <supportedlock/>
        </prop>
        <status>HTTP/1.1 200 OK</status>
        </propstat>
        </response>
        </multistatus>'''

        pfind = propfind.PROPFIND(folder, request)

        pfind.PROPFIND()
        # Check HTTP Response
        self.assertEqual(request.response.getStatus(), 207)
        self.assertEqual(pfind.getDepth(), 'infinity')
        s1 = normalize_xml(request.response._body)
        s2 = normalize_xml(expect)
        self.assertEqual(s1, s2)

def test_suite():
    return TestSuite((
        makeSuite(TestPlacefulPROPFIND),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
