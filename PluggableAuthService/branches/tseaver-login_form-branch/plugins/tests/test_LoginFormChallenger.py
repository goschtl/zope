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
     import IChallengePlugin_conformance

from Products.PluggableAuthService.tests.test_PluggableAuthService \
     import FauxRequest
from Products.PluggableAuthService.tests.test_PluggableAuthService \
     import FauxResponse
from Products.PluggableAuthService.tests.test_PluggableAuthService \
     import FauxObject
from Products.PluggableAuthService.tests.test_PluggableAuthService \
     import FauxRoot
from Products.PluggableAuthService.tests.test_PluggableAuthService \
     import FauxContainer

class FauxSettableRequest(FauxRequest):

    def set(self, name, value):
        self._dict[name] = value

class FauxRedirectResponse(FauxResponse):

    def __init__(self):
        self.redirected = False
        self.status = '200'
        self.headers = {}

    def redirect(self, location, status=302, lock=0):
        self.status = status
        self.headers['Location'] = location

class LoginFormChallengerTests( unittest.TestCase
                              , ILoginPasswordHostExtractionPlugin_conformance
                              , IChallengePlugin_conformance
                              ):

    def _getTargetClass( self ):

        from Products.PluggableAuthService.plugins.LoginFormChallenger \
            import LoginFormChallenger

        return LoginFormChallenger

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
        response = FauxResponse()
        request = FauxRequest(RESPONSE=response)

        self.assertEqual( helper.extractCredentials( request ), {} )

    def test_extractCredentials_with_form_creds( self ):

        helper = self._makeOne()
        response = FauxResponse()
        request = FauxSettableRequest(__ac_name='foo',
                                      __ac_password='bar',
                                      RESPONSE=response)

        self.assertEqual(helper.extractCredentials(request),
                        {'login': 'foo',
                         'password': 'bar',
                         'remote_host': '',
                         'remote_address': ''})

    def test_challenge_simple( self ):
        rc, root, folder, object = self._makeTree()
        response = FauxRedirectResponse()
        request = FauxRequest(RESPONSE=response)
        root.REQUEST = request

        helper = self._makeOne().__of__(root)

        helper.challenge(request, response)

        self.assertEqual(response.status, 302)
        self.assertEqual(len(response.headers), 1)
        self.assertEqual(response.headers['Location'], '/login_form')

    def test_challenge_came_from( self ):

        from urllib import unquote_plus

        CAME_FROM = '/some/protected/resource'

        rc, root, folder, object = self._makeTree()
        response = FauxRedirectResponse()
        request = FauxRequest(RESPONSE=response, URL=CAME_FROM)
        root.REQUEST = request

        helper = self._makeOne().__of__(root)

        helper.challenge(request, response)

        self.assertEqual(response.status, 302)
        self.assertEqual(len(response.headers), 1)
        self.assertEqual(unquote_plus(response.headers['Location']),
                         '/login_form?came_from=%s' % CAME_FROM)

    def test_challenge_preserves_query( self ):

        QUERY_STRING = 'foo=1&bar=yes'

        rc, root, folder, object = self._makeTree()
        response = FauxRedirectResponse()
        request = FauxRequest(QUERY_STRING=QUERY_STRING, RESPONSE=response)
        root.REQUEST = request

        helper = self._makeOne().__of__(root)

        helper.challenge(request, response)

        self.assertEqual(response.status, 302)
        self.assertEqual(len(response.headers), 1)
        self.assertEqual(response.headers['Location'],
                         '/login_form?%s' % QUERY_STRING)

    def test_challenge_came_from_and_query( self ):

        from urllib import unquote_plus

        CAME_FROM = '/some/protected/resource'
        QUERY_STRING = 'foo=1&bar=yes'

        rc, root, folder, object = self._makeTree()
        response = FauxRedirectResponse()
        request = FauxRequest(RESPONSE=response, URL=CAME_FROM,
                              QUERY_STRING=QUERY_STRING)
        root.REQUEST = request

        helper = self._makeOne().__of__(root)

        helper.challenge(request, response)

        self.assertEqual(response.status, 302)
        self.assertEqual(len(response.headers), 1)
        self.assertEqual(unquote_plus(response.headers['Location']),
                         '/login_form?came_from=%s&%s'
                            % (CAME_FROM, QUERY_STRING))

if __name__ == "__main__":
    unittest.main()

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite( LoginFormChallengerTests ),
        ))

