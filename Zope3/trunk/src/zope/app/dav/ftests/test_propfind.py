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
"""Functional tests for PROPFIND.

$Id$
"""
import unittest
from datetime import datetime
from transaction import get_transaction
from zope.pagetemplate.tests.util import normalize_xml

from zope.app import zapi
from zope.app.dav.ftests.dav import DAVTestCase
from zope.app.dublincore.interfaces import IZopeDublinCore
from zope.app.traversing.api import traverse

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
        get_transaction().commit()
        self.verifyPropOK(path='/pt', ns='http://purl.org/dc/1.1',
                          prop='title', expect='Test Title', basic='mgr:mgrpw')

    def test_dccreated(self):
        self.addPage('/pt', u'<span />')
        pt = traverse(self.getRootFolder(), '/pt')
        adapted = IZopeDublinCore(pt)
        adapted.created = datetime.utcnow()
        get_transaction().commit()
        expect = str(adapted.created)
        self.verifyPropOK(path='/pt', ns='http://purl.org/dc/1.1',
                          prop='created', expect=expect, basic='mgr:mgrpw')

    def test_dcsubject(self):
        self.addPage('/pt', u'<span />')
        pt = traverse(self.getRootFolder(), '/pt')
        adapted = IZopeDublinCore(pt)
        adapted.subjects = (u'Bla', u'Ble', u'Bli')
        get_transaction().commit()
        expect = ', '.join(adapted.subjects)
        self.verifyPropOK(path='/pt', ns='http://purl.org/dc/1.1',
                          prop='subjects', expect=expect, basic='mgr:mgrpw')

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
        s2 = normalize_xml("""<?xml version="1.0" ?>
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
    suite.addTest(unittest.makeSuite(TestPROPFIND))
    return suite


if __name__ == '__main__':
    unittest.main()
