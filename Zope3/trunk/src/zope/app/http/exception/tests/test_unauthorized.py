##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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

Revision information:
$Id: test_unauthorized.py,v 1.1 2003/03/29 17:03:59 sidnei Exp $
"""

from unittest import TestCase, main, makeSuite
from zope.publisher.browser import TestRequest
from zope.app.interfaces.http import IHTTPException

class Test(TestCase):

    def testbasicauth(self):
        from zope.app.http.exception.unauthorized import Unauthorized
        exception = Exception()
        try:
            raise exception
        except:
            pass
        request = TestRequest('/')
        u = Unauthorized(exception, request)

        # Chech that we implement the right interface
        self.failUnless(IHTTPException.isImplementedBy(u))
        
        # Call the view
        u()
        
        # Make sure the response status was set
        self.assertEqual(request.response.getStatus(), 401)
        self.failUnless(request.response.getHeader('WWW-Authenticate', '', True).startswith('basic'))

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
