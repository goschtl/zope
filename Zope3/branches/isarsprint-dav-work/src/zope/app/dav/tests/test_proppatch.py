##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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

$Id: test_directives.py 27844 2004-10-09 15:37:29Z mj $
"""
__docformat__ = 'restructuredtext'

import unittest
from StringIO import StringIO

from zope.interface import Interface, implements, directlyProvides
from zope.publisher.interfaces.http import IHTTPRequest
	
from zope.app import zapi
from zope.app.tests import ztapi

from zope.app.traversing.api import traverse
from zope.publisher.browser import TestRequest
from zope.app.site.tests.placefulsetup import PlacefulSetup
from zope.app.traversing.browser import AbsoluteURL
from zope.app.dublincore.interfaces import IZopeDublinCore
from zope.app.dublincore.annotatableadapter import ZDCAnnotatableAdapter
from zope.app.annotation.interfaces import IAnnotatable, IAnnotations
from zope.app.annotation.attribute import AttributeAnnotations

import zope.app.dav.tests
from zope.app.dav.tests.unitfixtures import File, Folder, FooZPT

from zope.app.dav import proppatch
from zope.app.dav.interfaces import IDAVSchema
from zope.app.dav.interfaces import IDAVNamespace

def _createRequest(body=None, headers=None, skip_headers=None,
                   namespaces=(('Z', 'http://www.w3.com/standards/z39.50/'),),
                   set=('<Z:authors>\n<Z:Author>Jim Whitehead</Z:Author>\n',
                        '<Z:Author>Roy Fielding</Z:Author>\n</Z:authors>'),
                   remove=('<D:prop><Z:Copyright-Owner/></D:prop>\n')):
    if body is None:
        setProps = removeProps = ''
        if set:
            setProps = '<set><prop>\n%s\n</prop></set>\n' % (''.join(set))
        if remove:
            removeProps = '<remove><prop>\n%s\n</prop></remove>\n' % (
                ''.join(remove))
            
        body = '''<?xml version="1.0"  ?>

        <propertyupdate xmlns="DAV:"
                        xmlns:Z="http://www.w3.com/standards/z39.50/">
        %s
        </propertyupdate>
        ''' % (setProps + removeProps)

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

    
def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(PropFindTests),
        ))

if __name__ == '__main__':
    unittest.main()
