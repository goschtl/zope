##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Functional tests for the functional test framework

$Id: functional.py 26214 2004-07-08 19:00:07Z srichter $
"""
__docformat__ = 'restructuredtext'

import unittest
from zope.app.tests.functional import SampleFunctionalTest, BrowserTestCase
from zope.app.tests.functional import FunctionalDocFileSuite

class CookieFunctionalTest(BrowserTestCase):

    """Functional tests should handle cookies like a web browser
    
    Multiple requests in the same test should acumulate cookies.
    We also ensure that cookies with path values are only sent for
    the correct URL's so we can test cookies don't 'leak'. Expiry,
    secure and other cookie attributes are not being worried about
    at the moment

    """

    def setUp(self):
        super(CookieFunctionalTest, self).setUp()
        self.assertEqual(
                len(self.cookies.keys()), 0,
                'cookies store should be empty'
                )

        root = self.getRootFolder()

        from zope.app.zptpage.zptpage import ZPTPage

        page = ZPTPage()
        page.evaluateInlineCode = True
        page.source = u'''<script type="text/server-python">
            cookies = ['%s=%s'%(k,v) for k,v in request.getCookies().items()]
            cookies.sort()
            print ';'.join(cookies)
            </script>'''
        root['getcookies'] = page

        page = ZPTPage()
        page.evaluateInlineCode = True
        page.source = u'''<script type="text/server-python">
            request.response.setCookie('bid','bval')
            </script>'''
        root['setcookie'] = page


    def tearDown(self):
        root = self.getRootFolder()
        del root['getcookies']
        del root['setcookie']
        super(CookieFunctionalTest, self).tearDown()

    def testDefaultCookies(self):
        # By default no cookies are set
        response = self.publish('/')
        self.assertEquals(response.getStatus(), 200)
        self.assert_(not response._request._cookies)

    def testSimpleCookies(self):
        self.cookies['aid'] = 'aval'
        response = self.publish('/')
        self.assertEquals(response.getStatus(), 200)
        self.assertEquals(response._request._cookies['aid'], 'aval')

    def testCookiePaths(self):
        # We only send cookies if the path is correct
        self.cookies['aid'] = 'aval'
        self.cookies['aid']['Path'] = '/sub/folder'
        self.cookies['bid'] = 'bval'
        response = self.publish('/')

        self.assertEquals(response.getStatus(), 200)
        self.assert_(not response._request._cookies.has_key('aid'))
        self.assertEquals(response._request._cookies['bid'], 'bval')

    def testHttpCookieHeader(self):
        # Passing an HTTP_COOKIE header to publish adds cookies
        response = self.publish('/', env={
            'HTTP_COOKIE': '$Version=1, aid=aval; $Path=/sub/folder, bid=bval'
            })
        self.assertEquals(response.getStatus(), 200)
        self.failIf(response._request._cookies.has_key('aid'))
        self.assertEquals(response._request._cookies['bid'], 'bval')

    def testStickyCookies(self):
        # Cookies should acumulate during the test
        response = self.publish('/', env={'HTTP_COOKIE': 'aid=aval;'})
        self.assertEquals(response.getStatus(), 200)

        # Cookies are implicity passed to further requests in this test
        response = self.publish('/getcookies')
        self.assertEquals(response.getStatus(), 200)
        self.assertEquals(response.getBody().strip(), 'aid=aval')

        # And cookies set in responses also acumulate
        response = self.publish('/setcookie')
        self.assertEquals(response.getStatus(), 200)
        response = self.publish('/getcookies')
        self.assertEquals(response.getStatus(), 200)
        self.assertEquals(response.getBody().strip(), 'aid=aval;bid=bval')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SampleFunctionalTest))
    suite.addTest(unittest.makeSuite(CookieFunctionalTest))
    suite.addTest(FunctionalDocFileSuite('doctest.txt'))
    return suite


if __name__ == '__main__':
    unittest.main()
