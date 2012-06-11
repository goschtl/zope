##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
"""Test the dav PROPPATCH interactions.
"""
import unittest
from StringIO import StringIO

import transaction
from ZODB.tests.util import DB

import zope.component
from zope.interface import Interface, implements, directlyProvides
from zope.schema import Text
from zope.schema.interfaces import IText, ISequence
from zope.publisher.interfaces.http import IHTTPRequest
from zope.publisher.http import status_reasons
from zope.publisher.browser import TestRequest
from zope.pagetemplate.tests.util import normalize_xml
from zope.traversing.api import traverse
from zope.traversing.browser import AbsoluteURL, absoluteURL
from zope.annotation.interfaces import IAnnotatable, IAnnotations
from zope.annotation.attribute import AttributeAnnotations
from zope.dublincore.interfaces import IZopeDublinCore
from zope.dublincore.annotatableadapter import ZDCAnnotatableAdapter
from zope.dublincore.zopedublincore import ScalarProperty

from zope.app.testing import ztapi
from zope.app.component.testing import PlacefulSetup

from zope.app.dav.tests.unitfixtures import File, Folder, FooZPT
from zope.app.dav import proppatch
from zope.app.dav.interfaces import IDAVSchema, IDAVNamespace, IDAVWidget
from zope.app.dav.widget import TextDAVWidget, SequenceDAVWidget
from zope.app.dav.opaquenamespaces import DAVOpaqueNamespacesAdapter
from zope.app.dav.opaquenamespaces import IDAVOpaqueNamespaces

def _createRequest(body=None, headers=None, skip_headers=None,
                   namespaces=(('Z', 'http://www.w3.com/standards/z39.50/'),),
                   set=('<Z:authors>\n<Z:Author>Jim Whitehead</Z:Author>\n',
                        '<Z:Author>Roy Fielding</Z:Author>\n</Z:authors>'),
                   remove=('<Z:Copyright-Owner/>'), extra=''):
    if headers is None:
        headers = {'Content-type':'text/xml'}
    if body is None:
        nsAttrs = setProps = removeProps = ''
        if set:
            setProps = '<set><prop>\n%s\n</prop></set>\n' % (''.join(set))
        if remove:
            removeProps = '<remove><prop>\n%s\n</prop></remove>\n' % (
                ''.join(remove))
        for prefix, ns in namespaces:
            nsAttrs += ' xmlns:%s="%s"' % (prefix, ns)

        body = '''<?xml version="1.0" encoding="utf-8"?>

        <propertyupdate xmlns="DAV:"%s>
        %s
        </propertyupdate>
        ''' % (nsAttrs, setProps + removeProps + extra)

    _environ = {'CONTENT_TYPE': 'text/xml',
                'CONTENT_LENGTH': str(len(body))}

    if headers is not None:
        for key, value in headers.items():
            _environ[key.upper().replace("-", "_")] = value

    if skip_headers is not None:
        for key in skip_headers:
            if _environ.has_key(key.upper()):
                del _environ[key.upper()]

    request = TestRequest(StringIO(body), _environ)
    return request


class ITestSchema(Interface):
    requiredNoDefault = Text(required=True, default=None)
    requiredDefault = Text(required=True, default=u'Default Value')
    unusualMissingValue = Text(required=False, missing_value=u'Missing Value')
    constrained = Text(required=False, min_length=5)

EmptyTestValue = object()
TestKey = 'zope.app.dav.tests.test_proppatch'
TestURI = 'uri://proppatch_tests'

class TestSchemaAdapter(object):
    implements(ITestSchema)
    __used_for__ = IAnnotatable
    annotations = None

    def __init__(self, context):
        annotations = IAnnotations(context)
        data = annotations.get(TestKey)
        if data is None:
            self.annotations = annotations
            data =  {u'requiredNoDefault': (EmptyTestValue,),
                     u'requiredDefault': (EmptyTestValue,),
                     u'unusualMissingValue': (EmptyTestValue,),
                     u'constrained': (EmptyTestValue,)}
        self._mapping = data

    def _changed(self):
        if self.annotations is not None:
            self.annotations[TestKey] = self._mapping
            self.annotations = None

    requiredNoDefault = ScalarProperty(u'requiredNoDefault')
    requiredDefault = ScalarProperty(u'requiredDefault')
    unusualMissingValue = ScalarProperty(u'unusualMissingValue')
    constrained = ScalarProperty(u'constrained')


class PropFindTests(PlacefulSetup, unittest.TestCase):

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
                          'PROPPATCH', proppatch.PROPPATCH)
        ztapi.browserViewProviding(IText, TextDAVWidget, IDAVWidget)
        ztapi.browserViewProviding(ISequence, SequenceDAVWidget, IDAVWidget)

        zope.component.provideAdapter(AttributeAnnotations, (IAnnotatable,))
        zope.component.provideAdapter(ZDCAnnotatableAdapter, (IAnnotatable,),
                                      IZopeDublinCore)
        zope.component.provideAdapter(DAVOpaqueNamespacesAdapter,
                                      (IAnnotatable,), IDAVOpaqueNamespaces)
        zope.component.provideAdapter(TestSchemaAdapter, (IAnnotatable,),
                                      ITestSchema)

        directlyProvides(IDAVSchema, IDAVNamespace)
        zope.component.provideUtility(IDAVSchema, IDAVNamespace, 'DAV:')

        directlyProvides(IZopeDublinCore, IDAVNamespace)
        zope.component.provideUtility(IZopeDublinCore, IDAVNamespace,
                                      'http://www.purl.org/dc/1.1')

        directlyProvides(ITestSchema, IDAVNamespace)
        zope.component.provideUtility(ITestSchema, IDAVNamespace, TestURI)

        self.db = DB()
        self.conn = self.db.open()
        root = self.conn.root()
        root['Application'] = self.rootFolder
        transaction.commit()

    def tearDown(self):
        transaction.abort()
        self.db.close()
        PlacefulSetup.tearDown(self)

    def test_contenttype1(self):
        file = self.file
        request = _createRequest(headers={'Content-type':'text/xml'})
        ppatch = proppatch.PROPPATCH(file, request)
        ppatch.PROPPATCH()
        # Check HTTP Response
        self.assertEqual(request.response.getStatus(), 207)

    def test_contenttype2(self):
        file = self.file
        request = _createRequest(headers={'Content-type':'application/xml'})

        ppatch = proppatch.PROPPATCH(file, request)
        ppatch.PROPPATCH()
        # Check HTTP Response
        self.assertEqual(request.response.getStatus(), 207)

    def test_contenttype3(self):
        # Check for an appropriate response when the content-type has
        # parameters, and that the major/minor parts are treated in a
        # case-insensitive way.
        file = self.file
        request = _createRequest(headers={'Content-type':
                                          'TEXT/XML; charset="utf-8"'})
        ppatch = proppatch.PROPPATCH(file, request)
        ppatch.PROPPATCH()
        # Check HTTP Response
        self.assertEqual(request.response.getStatus(), 207)

    def test_bad_contenttype(self):
        file = self.file
        request = _createRequest(headers={'Content-type':'text/foo'})

        ppatch = proppatch.PROPPATCH(file, request)
        ppatch.PROPPATCH()
        # Check HTTP Response
        self.assertEqual(request.response.getStatus(), 400)

    def test_no_contenttype(self):
        file = self.file
        request = _createRequest(skip_headers=('content-type'))

        ppatch = proppatch.PROPPATCH(file, request)
        ppatch.PROPPATCH()
        # Check HTTP Response
        self.assertEqual(request.response.getStatus(), 207)
        self.assertEqual(ppatch.content_type, 'text/xml')

    def test_noupdates(self):
        file = self.file
        request = _createRequest(namespaces=(), set=(), remove=())
        ppatch = proppatch.PROPPATCH(file, request)
        ppatch.PROPPATCH()
        # Check HTTP Response
        self.assertEqual(request.response.getStatus(), 422)

    def _checkProppatch(self, obj, ns=(), set=(), rm=(), extra='', expect=''):
        request = _createRequest(namespaces=ns, set=set, remove=rm,
                                 extra=extra)
        resource_url = absoluteURL(obj, request)
        expect = '''<?xml version="1.0" encoding="utf-8"?>
            <multistatus xmlns="DAV:"><response>
            <href>%%(resource_url)s</href>
            %s
            </response></multistatus>
            ''' % expect
        expect = expect % {'resource_url': resource_url}
        ppatch = proppatch.PROPPATCH(obj, request)
        ppatch.PROPPATCH()
        # Check HTTP Response
        self.assertEqual(request.response.getStatus(), 207)
        s1 = normalize_xml(request.response.consumeBody())
        s2 = normalize_xml(expect)
        self.assertEqual(s1, s2)

    def _makePropstat(self, ns, properties, status=200):
        nsattrs = ''
        count = 0
        for uri in ns:
            nsattrs += ' xmlns:a%d="%s"' % (count, uri)
            count += 1
        reason = status_reasons[status]
        return '''<propstat>
            <prop%s>%s</prop>
            <status>HTTP/1.1 %d %s</status>
            </propstat>''' % (nsattrs, properties, status, reason)

    def _assertOPropsEqual(self, obj, expect):
        oprops = IDAVOpaqueNamespaces(obj)
        namespacesA = list(oprops.keys())
        namespacesA.sort()
        namespacesB = expect.keys()
        namespacesB.sort()
        self.assertEqual(namespacesA, namespacesB,
                         'available opaque namespaces were %s, '
                         'expected %s' % (namespacesA, namespacesB))

        for ns in namespacesA:
            propnamesA = list(oprops[ns].keys())
            propnamesA.sort()
            propnamesB = expect[ns].keys()
            propnamesB.sort()
            self.assertEqual(propnamesA, propnamesB,
                             'props for opaque namespaces %s were %s, '
                             'expected %s' % (ns, propnamesA, propnamesB))
            for prop in propnamesA:
                valueA = oprops[ns][prop]
                valueB = expect[ns][prop]
                self.assertEqual(valueA, valueB,
                                 'opaque prop %s:%s was %s, '
                                 'expected %s' % (ns, prop, valueA, valueB))

    def test_removenonexisting(self):
        expect = self._makePropstat(('uri://foo',), '<bar xmlns="a0"/>')
        self._checkProppatch(self.zpt, ns=(('foo', 'uri://foo'),),
            rm=('<foo:bar />'), expect=expect)

    def test_opaque_set_simple(self):
        expect = self._makePropstat(('uri://foo',), '<bar xmlns="a0"/>')
        self._checkProppatch(self.zpt, ns=(('foo', 'uri://foo'),),
            set=('<foo:bar>spam</foo:bar>'), expect=expect)
        self._assertOPropsEqual(self.zpt,
                                {u'uri://foo': {u'bar': '<bar>spam</bar>'}})

    def test_opaque_remove_simple(self):
        oprops = IDAVOpaqueNamespaces(self.zpt)
        oprops['uri://foo'] = {'bar': '<bar>eggs</bar>'}
        expect = self._makePropstat(('uri://foo',), '<bar xmlns="a0"/>')
        self._checkProppatch(self.zpt, ns=(('foo', 'uri://foo'),),
            rm=('<foo:bar>spam</foo:bar>'), expect=expect)
        self._assertOPropsEqual(self.zpt, {})

    def test_opaque_add_and_replace(self):
        oprops = IDAVOpaqueNamespaces(self.zpt)
        oprops['uri://foo'] = {'bar': '<bar>eggs</bar>'}
        expect = self._makePropstat(
            ('uri://castle', 'uri://foo'),
            '<camelot xmlns="a0"/><bar xmlns="a1"/>')
        self._checkProppatch(self.zpt,
            ns=(('foo', 'uri://foo'), ('c', 'uri://castle')),
            set=('<foo:bar>spam</foo:bar>',
                 '<c:camelot place="silly" xmlns:k="uri://knights">'
                 '  <k:roundtable/>'
                 '</c:camelot>'),
            expect=expect)
        self._assertOPropsEqual(self.zpt, {
            u'uri://foo': {u'bar': '<bar>spam</bar>'},
            u'uri://castle': {u'camelot':
                '<camelot place="silly" xmlns:p0="uri://knights">'
                '  <p0:roundtable/></camelot>'}})

    def test_opaque_set_and_remove(self):
        expect = self._makePropstat(
            ('uri://foo',), '<bar xmlns="a0"/>')
        self._checkProppatch(self.zpt, ns=(('foo', 'uri://foo'),),
            set=('<foo:bar>eggs</foo:bar>',), rm=('<foo:bar/>',),
            expect=expect)
        self._assertOPropsEqual(self.zpt, {})

    def test_opaque_complex(self):
        # PROPPATCH allows us to set, remove and set the same property, ordered
        expect = self._makePropstat(
            ('uri://foo',), '<bar xmlns="a0"/>')
        self._checkProppatch(self.zpt, ns=(('foo', 'uri://foo'),),
            set=('<foo:bar>spam</foo:bar>',), rm=('<foo:bar/>',),
            extra='<set><prop><foo:bar>spam</foo:bar></prop></set>',
            expect=expect)
        self._assertOPropsEqual(self.zpt,
                                {u'uri://foo': {u'bar': '<bar>spam</bar>'}})

    def test_proppatch_failure(self):
        expect = self._makePropstat(
            ('uri://foo',), '<bar xmlns="a0"/>', 424)
        expect += self._makePropstat(
            ('http://www.purl.org/dc/1.1',), '<nonesuch xmlns="a0"/>', 403)
        self._checkProppatch(self.zpt,
            ns=(('foo', 'uri://foo'), ('DC', 'http://www.purl.org/dc/1.1')),
            set=('<foo:bar>spam</foo:bar>', '<DC:nonesuch>Test</DC:nonesuch>'),
            expect=expect)
        self._assertOPropsEqual(self.zpt, {})

    def test_nonexistent_dc(self):
        expect = self._makePropstat(
            ('http://www.purl.org/dc/1.1',), '<nonesuch xmlns="a0"/>', 403)
        self._checkProppatch(self.zpt,
            ns=(('DC', 'http://www.purl.org/dc/1.1'),),
            set=('<DC:nonesuch>Test</DC:nonesuch>',), expect=expect)

    def test_set_readonly(self):
        expect = self._makePropstat((), '<getcontentlength/>', 409)
        self._checkProppatch(self.zpt,
            set=('<getcontentlength>Test</getcontentlength>',), expect=expect)

    def test_remove_readonly(self):
        expect = self._makePropstat((), '<getcontentlength/>', 409)
        self._checkProppatch(self.zpt, rm=('<getcontentlength/>',),
                             expect=expect)

    def test_remove_required_no_default(self):
        testprops = ITestSchema(self.zpt)
        testprops.requiredNoDefault = u'foo'
        transaction.commit()
        expect = self._makePropstat((TestURI,),
                                    '<requiredNoDefault xmlns="a0"/>', 409)
        self._checkProppatch(self.zpt,
            ns=(('tst', TestURI),), rm=('<tst:requiredNoDefault/>',),
            expect=expect)
        self.assertEqual(ITestSchema(self.zpt).requiredNoDefault, u'foo')

    def test_remove_required_default(self):
        testprops = ITestSchema(self.zpt)
        testprops.requiredDefault = u'foo'
        transaction.commit()
        expect = self._makePropstat((TestURI,),
                                    '<requiredDefault xmlns="a0"/>', 200)
        self._checkProppatch(self.zpt,
            ns=(('tst', TestURI),), rm=('<tst:requiredDefault/>',),
            expect=expect)
        self.assertEqual(testprops.requiredDefault, u'Default Value')

    def test_remove_required_missing_value(self):
        testprops = ITestSchema(self.zpt)
        testprops.unusualMissingValue = u'foo'
        transaction.commit()
        expect = self._makePropstat((TestURI,),
                                    '<unusualMissingValue xmlns="a0"/>', 200)
        self._checkProppatch(self.zpt,
            ns=(('tst', TestURI),), rm=('<tst:unusualMissingValue/>',),
            expect=expect)
        self.assertEqual(testprops.unusualMissingValue, u'Missing Value')

    def test_set_dctitle(self):
        dc = IZopeDublinCore(self.zpt)
        dc.title = u'Test Title'
        transaction.commit()
        expect = self._makePropstat(('http://www.purl.org/dc/1.1',),
                                    '<title xmlns="a0"/>', 200)
        self._checkProppatch(self.zpt,
            ns=(('DC', 'http://www.purl.org/dc/1.1'),),
            set=('<DC:title>Foo Bar</DC:title>',),
            expect=expect)
        self.assertEqual(dc.title, u'Foo Bar')

    def test_set_dcsubjects(self):
        dc = IZopeDublinCore(self.zpt)
        dc.subjects = (u'Bla', u'Ble', u'Bli')
        transaction.commit()
        expect = self._makePropstat(('http://www.purl.org/dc/1.1',),
                                    '<subjects xmlns="a0"/>', 200)
        self._checkProppatch(self.zpt,
            ns=(('DC', 'http://www.purl.org/dc/1.1'),),
            set=('<DC:subjects>Foo, Bar</DC:subjects>',),
            expect=expect)
        self.assertEqual(dc.subjects, (u'Foo', u'Bar'))

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(PropFindTests),
        ))

if __name__ == '__main__':
    unittest.main()
