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
"""Functional tests for virtual hosting.

$Id: test_propfind.py,v 1.2 2003/05/22 15:10:58 sidnei Exp $
"""

import unittest
from datetime import datetime
from zope.testing.functional import HTTPTestCase
from zope.app.content.zpt import ZPTPage
from zope.app.content.folder import Folder
from transaction import get_transaction
from zope.pagetemplate.tests.util import normalize_xml
from zope.component import getAdapter
from zope.app.interfaces.dublincore import IZopeDublinCore
from zope.app.traversing import traverse

__metaclass__ = type

class TestPROPFIND(HTTPTestCase):

    def test_dctitle(self):
        self.addPage('/pt', u'<span />')
        self.verifyPropOK(path='/pt', ns='http://purl.org/dc/1.1',
                          prop='title', expect='', basic='mgr:mgrpw')

    def test_dctitle2(self):
        self.addPage('/pt', u'<span />')
        pt = traverse(self.getRootFolder(), '/pt')
        adapted = getAdapter(pt, IZopeDublinCore)
        adapted.title = u'Test Title'
        get_transaction().commit()
        self.verifyPropOK(path='/pt', ns='http://purl.org/dc/1.1',
                          prop='title', expect='Test Title', basic='mgr:mgrpw')

    def test_dccreated(self):
        self.addPage('/pt', u'<span />')
        pt = traverse(self.getRootFolder(), '/pt')
        adapted = getAdapter(pt, IZopeDublinCore)
        adapted.created = datetime.utcnow()
        get_transaction().commit()
        expect = str(adapted.created)
        self.verifyPropOK(path='/pt', ns='http://purl.org/dc/1.1',
                          prop='created', expect=expect, basic='mgr:mgrpw')

    def test_dcsubject(self):
        self.addPage('/pt', u'<span />')
        pt = traverse(self.getRootFolder(), '/pt')
        adapted = getAdapter(pt, IZopeDublinCore)
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

    def createFolders(self, path):
        """addFolders('/a/b/c/d') would traverse and/or create three nested
        folders (a, b, c) and return a tuple (c, 'd') where c is a Folder
        instance at /a/b/c."""
        folder = self.getRootFolder()
        if path[0] == '/':
            path = path[1:]
        path = path.split('/')
        for id in path[:-1]:
            try:
                folder = folder[id]
            except KeyError:
                folder.setObject(id, Folder())
                folder = folder[id]
        return folder, path[-1]

    def createObject(self, path, obj):
        folder, id = self.createFolders(path)
        folder.setObject(id, obj)
        get_transaction().commit()

    def addPage(self, path, content):
        page = ZPTPage()
        page.source = content
        self.createObject(path, page)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPROPFIND))
    return suite


if __name__ == '__main__':
    unittest.main()
