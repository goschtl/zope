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
"""Test HTTP PUT verb

$Id$
"""

from unittest import TestSuite, TestCase, makeSuite

from zope.app.wsgi.testlayer import http, BrowserLayer
import zope.app.http

layer = BrowserLayer(zope.app.http)

class TestPUT(TestCase):    
    def test_put(self):
        # PUT something for the first time
        out = http(r"""PUT /testfile.txt HTTP/1.1
Authorization: Basic globalmgr:globalmgrpw
X-Zope-Handle-Errors: False
Content-Length: 20
Content-Type: text/plain

This is just a test.""")
        self.assertEquals(
            out,
            ('HTTP/1.0 201 Created\n'
             'X-Powered-By: Zope (www.zope.org), Python (www.python.org)\n'
             'Content-Length: 0\n'
             'Location: http://localhost/testfile.txt\n\n'))
            
        out = http(r"""GET /testfile.txt HTTP/1.1
Authorization: Basic globalmgr:globalmgrpw""")
        self.assertEquals(out.split('\n\n')[1],
                          'This is just a test.')
    
        # now modify it
        out = http(r"""PUT /testfile.txt HTTP/1.1
Authorization: Basic globalmgr:globalmgrpw
Content-Length: 23
Content-Type: text/plain

And now it is modified.""")

        self.assert_('200' in out)
        self.assertEquals(out.split('\n\n')[1], "")
    
        out = http(r"""GET /testfile.txt HTTP/1.1
Authorization: Basic globalmgr:globalmgrpw""")

        self.assertEquals(out.split('\n\n')[1], "And now it is modified.")
        
def test_suite():
    TestPUT.layer = layer
    return TestSuite((
        makeSuite(TestPUT),
        ))
