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

from zope.interface import Interface,  directlyProvides
from zope.publisher.interfaces.http import IHTTPRequest

from zope.pagetemplate.tests.util import normalize_xml
from zope.schema import getFieldNamesInOrder
from zope.schema.interfaces import IText, ITextLine, IDatetime, ISequence

from zope.app import zapi
from zope.app.testing import ztapi

from zope.app.traversing.api import traverse
from zope.app.container.interfaces import IReadContainer
from zope.publisher.browser import TestRequest
from zope.app.component.testing import PlacefulSetup
from zope.app.traversing.browser import AbsoluteURL
from zope.app.dublincore.interfaces import IZopeDublinCore
from zope.app.dublincore.annotatableadapter import ZDCAnnotatableAdapter
from zope.app.annotation.interfaces import IAnnotatable, IAnnotations
from zope.app.annotation.attribute import AttributeAnnotations

from zope.app.dav import propfind
from zope.app.dav.interfaces import IDAVSchema
from zope.app.dav.interfaces import IDAVNamespace
from zope.app.dav.interfaces import IDAVWidget
from zope.app.dav.widget import TextDAVWidget, SequenceDAVWidget
from zope.app.dav.opaquenamespaces import DAVOpaqueNamespacesAdapter
from zope.app.dav.opaquenamespaces import IDAVOpaqueNamespaces
from zope.app.dav.adapter import DAVSchemaAdapter

from unitfixtures import File, Folder, FooZPT


def _createRequest(body=None, headers=None, skip_headers=None):
    if body is None:
        body = '''<?xml version="1.0" encoding="utf-8"?>

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
        ztapi.provideView(None, IHTTPRequest, Interface,
                          'absolute_url', AbsoluteURL)
        ztapi.provideView(None, IHTTPRequest, Interface,
                          'PROPFIND', propfind.PROPFIND)
        ztapi.browserViewProviding(IText, TextDAVWidget, IDAVWidget)
        ztapi.browserViewProviding(ITextLine, TextDAVWidget, IDAVWidget)
        ztapi.browserViewProviding(IDatetime, TextDAVWidget, IDAVWidget)
        ztapi.browserViewProviding(ISequence, SequenceDAVWidget, IDAVWidget)
        ztapi.provideAdapter(IAnnotatable, IAnnotations, AttributeAnnotations)
        ztapi.provideAdapter(IAnnotatable, IZopeDublinCore,
                             ZDCAnnotatableAdapter)
        ztapi.provideAdapter(IAnnotatable, IDAVOpaqueNamespaces,
                             DAVOpaqueNamespacesAdapter)
        ztapi.provideAdapter(None, IDAVSchema,
                             DAVSchemaAdapter)
        sm = zapi.getGlobalSiteManager()
        directlyProvides(IDAVSchema, IDAVNamespace)
        sm.provideUtility(IDAVNamespace, IDAVSchema, 'DAV:')
        directlyProvides(IZopeDublinCore, IDAVNamespace)
        sm.provideUtility(IDAVNamespace, IZopeDublinCore,
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

    def _checkPropfind(self, obj, req, expect, depth='0', resp=None):
        if req:
            body = '''<?xml version="1.0" ?>
            <propfind xmlns="DAV:">%s</propfind>
            ''' % req
        else:
            body = ''
        request = _createRequest(body=body, headers={
            'Content-type': 'text/xml', 'Depth': depth})
        resource_url = zapi.absoluteURL(obj, request)
        if IReadContainer.providedBy(obj):
            resource_url += '/'
        if resp is None:
            resp = '''<?xml version="1.0" encoding="utf-8"?>
            <multistatus xmlns="DAV:"><response>
            <href>%%(resource_url)s</href>
            <propstat>%s
            <status>HTTP/1.1 200 OK</status>
            </propstat></response></multistatus>
            '''
        expect = resp % expect
        expect = expect % {'resource_url': resource_url}
        pfind = propfind.PROPFIND(obj, request)
        pfind.PROPFIND()
        # Check HTTP Response
        self.assertEqual(request.response.getStatus(), 207)
        self.assertEqual(pfind.getDepth(), depth)
        s1 = normalize_xml(request.response._body)
        s2 = normalize_xml(expect)
        self.assertEqual(s1, s2)

    def test_davpropdctitle(self):
        root = self.rootFolder
        zpt = traverse(root, 'zpt')
        dc = IZopeDublinCore(zpt)
        dc.title = u'Test Title'
        req = '''<prop xmlns:DC="http://www.purl.org/dc/1.1">
        <DC:title />
        </prop>'''

        expect = '''<prop xmlns:a0="http://www.purl.org/dc/1.1">
        <title xmlns="a0">Test Title</title></prop>'''
        self._checkPropfind(zpt, req, expect)

    def test_davpropdccreated(self):
        root = self.rootFolder
        zpt = traverse(root, 'zpt')
        dc = IZopeDublinCore(zpt)
        dc.created = datetime.utcnow()
        req = '''<prop xmlns:DC="http://www.purl.org/dc/1.1">
        <DC:created /></prop>'''
        expect = '''<prop xmlns:a0="http://www.purl.org/dc/1.1">
        <created xmlns="a0">%s</created></prop>''' % dc.created
        self._checkPropfind(zpt, req, expect)

    def test_davpropdcsubjects(self):
        root = self.rootFolder
        zpt = traverse(root, 'zpt')
        dc = IZopeDublinCore(zpt)
        dc.subjects = (u'Bla', u'Ble', u'Bli')
        req = '''<prop xmlns:DC="http://www.purl.org/dc/1.1">
        <DC:subjects /></prop>'''

        expect = '''<prop xmlns:a0="http://www.purl.org/dc/1.1">
        <subjects xmlns="a0">%s</subjects></prop>''' % u', '.join(dc.subjects)
        self._checkPropfind(zpt, req, expect)

    def test_davpropname(self):
        root = self.rootFolder
        zpt = traverse(root, 'zpt')
        oprops = IDAVOpaqueNamespaces(zpt)
        oprops[u'http://foo/bar'] = {u'egg': '<egg>spam</egg>'}
        req = '''<propname/>'''

        expect = ''
        props = getFieldNamesInOrder(IZopeDublinCore)
        for p in props:
            expect += '<%s xmlns="a0"/>' % p
        expect += '<egg xmlns="a1"/>'
        props = getFieldNamesInOrder(IDAVSchema)
        for p in props:
            expect += '<%s/>' % p
        expect = '''
        <prop xmlns:a0="http://www.purl.org/dc/1.1" xmlns:a1="http://foo/bar">
        %s</prop>''' % expect
        self._checkPropfind(zpt, req, expect)

    def test_davpropnamefolderdepth0(self):
        root = self.rootFolder
        folder = traverse(root, 'folder')
        req = '''<propname/>'''

        expect = ''
        props = getFieldNamesInOrder(IZopeDublinCore)
        for p in props:
            expect += '<%s xmlns="a0"/>' % p
        props = getFieldNamesInOrder(IDAVSchema)
        for p in props:
            expect += '<%s/>' % p
        expect = '''<prop xmlns:a0="http://www.purl.org/dc/1.1">
        %s</prop>''' % expect
        self._checkPropfind(folder, req, expect)

    def test_davpropnamefolderdepth1(self):
        root = self.rootFolder
        folder = traverse(root, 'folder')
        req = '''<propname/>'''

        props_xml = ''
        props = getFieldNamesInOrder(IZopeDublinCore)
        for p in props:
            props_xml += '<%s xmlns="a0"/>' % p
        props = getFieldNamesInOrder(IDAVSchema)
        for p in props:
            props_xml += '<%s/>' % p

        expect = ''
        for p in ('', '1', '2', 'sub1/'):
            expect += '''
            <response><href>%(path)s</href>
            <propstat><prop xmlns:a0="http://www.purl.org/dc/1.1">
            %(props_xml)s</prop><status>HTTP/1.1 200 OK</status>
            </propstat></response>
            ''' % {'path': '%(resource_url)s' + p, 'props_xml': props_xml}

        resp = '''<?xml version="1.0" encoding="utf-8"?>
        <multistatus xmlns="DAV:">%s</multistatus>'''
        self._checkPropfind(folder, req, expect, depth='1', resp=resp)

    def test_davpropnamefolderdepthinfinity(self):
        root = self.rootFolder
        folder = traverse(root, 'folder')
        req = '''<propname/>'''

        props_xml = ''
        props = getFieldNamesInOrder(IZopeDublinCore)
        for p in props:
            props_xml += '<%s xmlns="a0"/>' % p
        props = getFieldNamesInOrder(IDAVSchema)
        for p in props:
            props_xml += '<%s/>' % p

        expect = ''
        for p in ('', '1', '2', 'sub1/', 'sub1/1', 'sub1/2', 'sub1/sub1/',
                  'sub1/sub1/last'):
            expect += '''
            <response><href>%(path)s</href>
            <propstat><prop xmlns:a0="http://www.purl.org/dc/1.1">
            %(props_xml)s</prop><status>HTTP/1.1 200 OK</status>
            </propstat></response>
            ''' % {'path': '%(resource_url)s' + p, 'props_xml': props_xml}

        resp = '''<?xml version="1.0" encoding="utf-8"?>
        <multistatus xmlns="DAV:">%s</multistatus>'''
        self._checkPropfind(folder, req, expect, depth='infinity', resp=resp)

    def test_davemptybodyallpropzptdepth0(self):
        # RFC 2518, Section 8.1: A client may choose not to submit a
        # request body.  An empty PROPFIND request body MUST be
        # treated as a request for the names and values of all
        # properties.

        root = self.rootFolder
        zpt = traverse(root, 'zpt')
        dc = IZopeDublinCore(zpt)
        dc.created = now = datetime.utcnow()

        req = ''
        expect = ''
        props = getFieldNamesInOrder(IZopeDublinCore)
        pvalues = {'created': '%s+00:00' % now}
        for p in props:
            if pvalues.has_key(p):
                expect += '<%s xmlns="a0">%s</%s>' % (p, pvalues[p], p)
            else:
                expect += '<%s xmlns="a0"></%s>' % (p, p)
        props = getFieldNamesInOrder(IDAVSchema)
        pvalues = {'displayname':'zpt',
                   'creationdate':now.strftime('%Y-%m-%d %TZ')}
        for p in props:
            if pvalues.has_key(p):
                expect += '<%s>%s</%s>' % (p, pvalues[p], p)
            else:
                expect += '<%s></%s>' % (p, p)
        expect = '''<prop xmlns:a0="http://www.purl.org/dc/1.1">
        %s</prop>''' % expect
        self._checkPropfind(zpt, req, expect)

    def test_propfind_opaque_simple(self):
        root = self.rootFolder
        zpt = traverse(root, 'zpt')
        oprops = IDAVOpaqueNamespaces(zpt)
        oprops[u'http://foo/bar'] = {u'egg': '<egg>spam</egg>'}
        req = '<prop xmlns:foo="http://foo/bar"><foo:egg /></prop>'

        expect = '''<prop xmlns:a0="http://foo/bar"><egg xmlns="a0">spam</egg>
        </prop>'''
        self._checkPropfind(zpt, req, expect)

    def test_propfind_opaque_complex(self):
        root = self.rootFolder
        zpt = traverse(root, 'zpt')
        oprops = IDAVOpaqueNamespaces(zpt)
        oprops[u'http://foo/bar'] = {u'egg':
            '<egg xmlns:bacon="http://bacon">\n'
            '  <bacon:pork>crispy</bacon:pork>\n'
            '</egg>\n'}
        req = '<prop xmlns:foo="http://foo/bar"><foo:egg /></prop>'

        expect = '''<prop xmlns:a0="http://foo/bar">
        <egg xmlns="a0" xmlns:bacon="http://bacon">
            <bacon:pork>crispy</bacon:pork>
        </egg></prop>'''
        self._checkPropfind(zpt, req, expect)

def test_suite():
    return TestSuite((
        makeSuite(TestPlacefulPROPFIND),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
