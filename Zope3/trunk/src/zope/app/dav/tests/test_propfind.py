##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""
$Id: test_propfind.py,v 1.6 2003/06/03 22:46:19 jim Exp $
"""
__metaclass__ = type

from datetime import datetime
from unittest import TestCase, TestSuite, main, makeSuite
from StringIO import StringIO
from zope.component import getService, getView, getAdapter
from zope.app.services.servicenames import Adapters, Views
from zope.app.traversing import traverse
from zope.publisher.browser import TestRequest
from zope.app.interfaces.file import IWriteFile
from zope.app.interfaces.content.zpt import IZPTPage
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.publisher.interfaces.http import IHTTPPresentation
from zope.app.browser.absoluteurl import AbsoluteURL
from zope.pagetemplate.tests.util import normalize_xml
from zope.schema import getFieldNamesInOrder
from zope.app.interfaces.container import IReadContainer
from zope.schema.interfaces import IText, ITextLine, IDatetime, ISequence
from zope.app.dav import propfind
from zope.app.interfaces.dav import IDAVSchema
from zope.app.dav.widget import TextDAVWidget, SequenceDAVWidget
from zope.app.dav.globaldavschemaservice import provideInterface
from zope.app.interfaces.dublincore import IZopeDublinCore
from zope.app.dublincore.annotatableadapter import ZDCAnnotatableAdapter
from zope.app.interfaces.annotation import IAnnotatable, IAnnotations
from zope.app.attributeannotations import AttributeAnnotations

class Folder:

    __implements__ = IReadContainer

    def __init__(self, name, level=0):
        self.name = name
        self.level=level

    def items(self):
        if self.level == 2:
            return (('last', File('last', 'text/plain', 'blablabla')),)
        result = []
        for i in range(1, 3):
            result.append((str(i), File(str(i), 'text/plain', 'blablabla')))
        result.append(('sub1', Folder('sub1', level=self.level+1)))
        return tuple(result)

class File:

    __implements__ = IWriteFile

    def __init__(self, name, content_type, data):
        self.name = name
        self.content_type = content_type
        self.data = data

    def write(self, data):
        self.data = data

class FooZPT:

    __implements__ = (IAnnotatable, IZPTPage)

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
            _environ[key.upper()] = value

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
        root.setObject('file', file)
        root.setObject('zpt', zpt)
        root.setObject('folder', folder)
        self.zpt = traverse(root, 'zpt')
        self.file = traverse(root, 'file')
        provideView = getService(None, Views).provideView
        setDefaultView = getService(None, Views).setDefaultViewName
        provideView(None, 'absolute_url', IHTTPPresentation,
                    [AbsoluteURL])
        provideView(None, 'PROPFIND', IHTTPPresentation,
                    [propfind.PROPFIND])
        provideView(IText, 'view', IBrowserPresentation,
                    [TextDAVWidget])
        provideView(ITextLine, 'view', IBrowserPresentation,
                    [TextDAVWidget])
        provideView(IDatetime, 'view', IBrowserPresentation,
                    [TextDAVWidget])
        provideView(ISequence, 'view', IBrowserPresentation,
                    [SequenceDAVWidget])
        setDefaultView(IText, IBrowserPresentation, 'view')
        setDefaultView(ITextLine, IBrowserPresentation, 'view')
        setDefaultView(IDatetime, IBrowserPresentation, 'view')
        setDefaultView(ISequence, IBrowserPresentation, 'view')
        provideAdapter = getService(None, Adapters).provideAdapter
        provideAdapter(IAnnotatable, IAnnotations, AttributeAnnotations)
        provideAdapter(IAnnotatable, IZopeDublinCore, ZDCAnnotatableAdapter)
        provideInterface('DAV:', IDAVSchema)
        provideInterface('http://www.purl.org/dc/1.1', IZopeDublinCore)

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

    def test_bad_contenttype(self):
        file = self.file
        request = _createRequest(headers={'Content-type':'text/foo'})

        pfind = propfind.PROPFIND(file, request)
        pfind.PROPFIND()
        # Check HTTP Response
        self.assertEqual(request.response.getStatus(), 207)

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
        dc = getAdapter(zpt, IZopeDublinCore)
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
        dc = getAdapter(zpt, IZopeDublinCore)
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
        dc = getAdapter(zpt, IZopeDublinCore)
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
