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
"""Functional tests for PROPPATCH.

$Id$
"""
import unittest
import transaction
from zope.pagetemplate.tests.util import normalize_xml
from zope.publisher.http import status_reasons
from zope.traversing.api import traverse
from zope.dublincore.interfaces import IZopeDublinCore

from zope.app.dav.tests.dav import DAVTestCase
from zope.app.dav.opaquenamespaces import IDAVOpaqueNamespaces
from zope.app.dav.testing import AppDavLayer

class TestPROPPATCH(DAVTestCase):

    def test_set(self):
        self.addPage('/pt', u'<span />')
        transaction.commit()
        expect = self._makePropstat(('uri://foo',), '<bar xmlns="a0"/>')
        self.verifyPropOK(path='/pt', namespaces=(('foo', 'uri://foo'),),
            set=('<foo:bar>spam</foo:bar>',), expect=expect)
        pt = traverse(self.getRootFolder(), '/pt')
        self._assertOPropsEqual(pt,
            {u'uri://foo': {u'bar': '<bar>spam</bar>'}})

    def test_remove(self):
        self.addPage('/pt', u'<span />')
        pt = traverse(self.getRootFolder(), '/pt')
        adapted = IDAVOpaqueNamespaces(pt)
        adapted[u'uri://foo'] = {u'bar': '<bar>spam</bar>'}
        transaction.commit()
        expect = self._makePropstat(('uri://foo',), '<bar xmlns="a0"/>')
        self.verifyPropOK(path='/pt', namespaces=(('foo', 'uri://foo'),),
            rm=('<foo:bar/>',), expect=expect)
        self._assertOPropsEqual(pt, {})

    def test_complex(self):
        self.addPage('/pt', u'<span />')
        pt = traverse(self.getRootFolder(), '/pt')
        adapted = IDAVOpaqueNamespaces(pt)
        adapted[u'uri://foo'] = {u'bar': '<bar>eggs</bar>'}
        adapted[u'uri://montypython'] = {u'castle': '<castle>camelot</castle>'}
        transaction.commit()
        expect = self._makePropstat(('uri://foo', 'uri://montypython'),
            '<bar xmlns="a0"/><castle xmlns="a1"/><song xmlns="a1"/>')
        self.verifyPropOK(path='/pt',
            namespaces=(('foo', 'uri://foo'), ('mp', 'uri://montypython')),
            set=('<foo:bar>spam</foo:bar>',),
            rm=('<mp:castle/>', '<mp:song/>'), expect=expect)
        self._assertOPropsEqual(pt,
            {u'uri://foo': {u'bar': '<bar>spam</bar>'}})

    def test_remove_dctitle(self):
        self.addPage('/pt', u'<span />')
        pt = traverse(self.getRootFolder(), '/pt')
        adapted = IZopeDublinCore(pt)
        adapted.title = u'Test'
        transaction.commit()
        # DC Title is a required field with no default, so a 409 is expected
        expect = self._makePropstat(('http://purl.org/dc/1.1',),
                                    '<title xmlns="a0"/>', 409)
        self.verifyPropOK(path='/pt',
            namespaces=(('DC', 'http://purl.org/dc/1.1'),),
            rm=('<DC:title/>',), expect=expect)

    def test_set_dctitle(self):
        self.addPage('/pt', u'<span />')
        pt = traverse(self.getRootFolder(), '/pt')
        adapted = IZopeDublinCore(pt)
        transaction.commit()
        expect = self._makePropstat(('http://purl.org/dc/1.1',),
                                    '<title xmlns="a0"/>')
        self.verifyPropOK(path='/pt',
            namespaces=(('DC', 'http://purl.org/dc/1.1'),),
            set=('<DC:title>Test Title</DC:title>',), expect=expect)
        self.assertEqual(IZopeDublinCore(pt).title, u'Test Title')

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

    def verifyPropOK(self, path, namespaces=(), set=(), rm=(), expect='',
                     basic='mgr:mgrpw'):
        nsAttrs = setProps = removeProps = ''
        if set:
            setProps = '<set><prop>\n%s\n</prop></set>\n' % (''.join(set))
        if rm:
            removeProps = '<remove><prop>\n%s\n</prop></remove>\n' % (
                ''.join(rm))
        for prefix, ns in namespaces:
            nsAttrs += ' xmlns:%s="%s"' % (prefix, ns)
        body = """<?xml version="1.0" encoding="utf-8"?>
        <propertyupdate xmlns="DAV:"%s>
        %s
        </propertyupdate>""" % (nsAttrs, setProps + removeProps)
        result = self.publish(path, basic, env={'REQUEST_METHOD':'PROPPATCH',
                                                'CONTENT-LENGHT': len(body)},
                              request_body=body)
        self.assertEquals(result.getStatus(), 207)
        s1 = normalize_xml(result.getBody())
        s2 = normalize_xml("""<?xml version="1.0" encoding="utf-8"?>
        <multistatus xmlns="DAV:">
        <response>
        <href>http://localhost/pt</href>
        %s
        </response>
        </multistatus>""" % expect)
        self.assertEquals(s1, s2)


def test_suite():
    suite = unittest.TestSuite()
    TestPROPPATCH.layer = AppDavLayer
    suite.addTest(unittest.makeSuite(TestPROPPATCH))
    return suite


if __name__ == '__main__':
    unittest.main()
