##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights
# Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this
# distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import unittest

from Products.PluggableAuthService.tests.conformance \
     import ILoginPasswordHostExtractionPlugin_conformance
from Products.PluggableAuthService.tests.conformance \
     import ICredentialsUpdatePlugin_conformance
from Products.PluggableAuthService.tests.conformance \
     import ICredentialsResetPlugin_conformance

from Products.PluggableAuthService.tests.test_PluggableAuthService \
     import FauxRequest, FauxResponse, FauxObject, FauxRoot, FauxContainer

class FauxSettableRequest(FauxRequest):

    def set(self, name, value):
        self._dict[name] = value

class FauxCookieResponse(FauxResponse):

    def __init__(self):
        self.cookies = {}
        self.redirected = False
        self.status = '200'
        self.headers = {}

    def setCookie(self, cookie_name, cookie_value, path):
        self.cookies[(cookie_name, path)] = cookie_value

    def expireCookie(self, cookie_name, path):
        if (cookie_name, path) in self.cookies:
            del self.cookies[(cookie_name, path)]

    def redirect(self, location, status=302, lock=0):
        self.status = status
        self.headers['Location'] = location

class CookieAuthHelperTests( unittest.TestCase
                           , ILoginPasswordHostExtractionPlugin_conformance
                           , ICredentialsResetPlugin_conformance
                           ):

    def _getTargetClass( self ):

        from Products.PluggableAuthService.plugins.CookieAuthHelper \
            import CookieAuthHelper

        return CookieAuthHelper

    def _makeOne( self, id='test', *args, **kw ):

        return self._getTargetClass()( id=id, *args, **kw )

    def _makeTree( self ):

        rc = FauxObject( 'rc' )
        root = FauxRoot( 'root' ).__of__( rc )
        folder = FauxContainer( 'folder' ).__of__( root )
        object = FauxObject( 'object' ).__of__( folder )

        return rc, root, folder, object

    def test_extractCredentials_no_creds( self ):

        helper = self._makeOne()
        response = FauxCookieResponse()
        request = FauxRequest(RESPONSE=response)

        self.assertEqual( helper.extractCredentials( request ), {} )

    def test_resetCredentials( self ):
        helper = self._makeOne()
        response = FauxCookieResponse()
        request = FauxRequest(RESPONSE=response)

        helper.resetCredentials(request, response)
        self.assertEqual(len(response.cookies), 0)


if __name__ == "__main__":
    unittest.main()

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite( CookieAuthHelperTests ),
        ))

