##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
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
"""Functional tests for PROPFIND.

$Id$
"""
import unittest
import transaction
from datetime import datetime
from zope.pagetemplate.tests.util import normalize_xml
from zope.traversing.api import traverse
from zope.dublincore.interfaces import IZopeDublinCore

from zope.app.dav.tests.dav import DAVTestCase
from zope.app.dav.opaquenamespaces import IDAVOpaqueNamespaces
from zope.app.dav.testing import AppDavLayer

class TestPROPFIND(DAVTestCase):

    def test_dctitle(self):
        self.addPage('/pt', u'<span />')
        self.verifyPropOK(path='/pt', ns='http://purl.org/dc/1.1',
                          prop='title', expect='', basic='mgr:mgrpw')

    def test_dctitle2(self):
        self.addPage('/pt', u'<span />')
        pt = traverse(self.getRootFolder(), '/pt')
        adapted = IZopeDublinCore(pt)
        adapted.title = u'Test Title'
        transaction.commit()
        self.verifyPropOK(path='/pt', ns='http://purl.org/dc/1.1',
                          prop='title', expect='Test Title', basic='mgr:mgrpw')

    def test_dccreated(self):
        self.addPage('/pt', u'<span />')
        pt = traverse(self.getRootFolder(), '/pt')
        adapted = IZopeDublinCore(pt)
        adapted.created = datetime.utcnow()
        transaction.commit()
        expect = str(adapted.created)
        self.verifyPropOK(path='/pt', ns='http://purl.org/dc/1.1',
                          prop='created', expect=expect, basic='mgr:mgrpw')

    def test_dcsubject(self):
        self.addPage('/pt', u'<span />')
        pt = traverse(self.getRootFolder(), '/pt')
        adapted = IZopeDublinCore(pt)
        adapted.subjects = (u'Bla', u'Ble', u'Bli')
        transaction.commit()
        expect = ', '.join(adapted.subjects)
        self.verifyPropOK(path='/pt', ns='http://purl.org/dc/1.1',
                          prop='subjects', expect=expect, basic='mgr:mgrpw')

    def test_opaque(self):
        self.addPage('/pt', u'<span />')
        pt = traverse(self.getRootFolder(), '/pt')
        adapted = IDAVOpaqueNamespaces(pt)
        adapted[u'uri://bar'] = {u'foo': '<foo>spam</foo>'}
        transaction.commit()
        expect = 'spam'
        self.verifyPropOK(path='/pt', ns='uri://bar',
                          prop='foo', expect=expect, basic='mgr:mgrpw')

    def verifyPropOK(self, path, ns, prop, expect, basic):
        body = """<?xml version="1.0" ?>
        <propfind xmlns="DAV:">
        <prop xmlns:a0="%(ns)s">
        <a0:%(prop)s />
        </prop>
        </propfind>""" % {'ns':ns, 'prop':prop}
        clen = len(body)
        result = self.publish(path, basic, env={'REQUEST_METHOD':'PROPFIND',
                                                'CONTENT-LENGHT': clen},
                              request_body=body)
        self.assertEquals(result.getStatus(), 207)
        s1 = normalize_xml(result.getBody())
        s2 = normalize_xml("""<?xml version="1.0" encoding="utf-8"?>
        <multistatus xmlns="DAV:">
        <response>
        <href>http://localhost/pt</href>
        <propstat>
        <prop xmlns:a0="%(ns)s">
        <%(prop)s xmlns="a0">%(expect)s</%(prop)s>
        </prop>
        <status>HTTP/1.1 200 OK</status>
        </propstat>
        </response>
        </multistatus>""" % {'ns':ns, 'prop':prop, 'expect':expect})
        self.assertEquals(s1, s2)


def test_suite():
    suite = unittest.TestSuite()
    TestPROPFIND.layer = AppDavLayer
    suite.addTest(unittest.makeSuite(TestPROPFIND))
    return suite


if __name__ == '__main__':
    unittest.main()
