##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights
# Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this
# distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
import unittest
from conformance import ILoginPasswordHostExtractionPlugin_conformance
from conformance import IChallengePlugin_conformance
from conformance import ICredentialsUpdatePlugin_conformance
from conformance import ICredentialsResetPlugin_conformance

class FauxHTTPRequest:

    def __init__( self, name=None, password=None ):

        self._name = name
        self._password = password

    def _authUserPW( self ):

        if self._name is None:
            return None

        return self._name, self._password

class FauxHTTPResponse:

    _unauthorized_called = 0

    def unauthorized( self ):

        self._unauthorized_called = 1

class HTTPBasicAuthHelperTests( unittest.TestCase
                              , ILoginPasswordHostExtractionPlugin_conformance
                              , IChallengePlugin_conformance
                              , ICredentialsUpdatePlugin_conformance
                              , ICredentialsResetPlugin_conformance
                              ):

    def _getTargetClass( self ):

        from Products.PluggableAuthService.plugins.HTTPBasicAuthHelper \
            import HTTPBasicAuthHelper

        return HTTPBasicAuthHelper

    def _makeOne( self, id='test', *args, **kw ):

        return self._getTargetClass()( id=id, *args, **kw )

    def test_extractCredentials_no_creds( self ):

        helper = self._makeOne()
        request = FauxHTTPRequest()

        self.assertEqual( helper.extractCredentials( request ), {} )

    def test_extractCredentials_with_creds( self ):

        helper = self._makeOne()
        request = FauxHTTPRequest( 'foo', 'bar' )

        self.assertEqual( helper.extractCredentials( request )
                        , { 'login' : 'foo', 'password' : 'bar' } )

    def test_challenge( self ):

        helper = self._makeOne()
        request = FauxHTTPRequest()
        response = FauxHTTPResponse()

        self.failIf( response._unauthorized_called )
        helper.challenge( request, response )
        self.failUnless( response._unauthorized_called )

    def test_updateCredentials( self ):

        helper = self._makeOne()
        request = FauxHTTPRequest()
        response = FauxHTTPResponse()

        self.failIf( response._unauthorized_called )
        helper.updateCredentials( request, response, new_password='baz' )
        self.failIf( response._unauthorized_called )

    def test_resetCredentials( self ):

        helper = self._makeOne()
        request = FauxHTTPRequest()
        response = FauxHTTPResponse()

        self.failIf( response._unauthorized_called )
        helper.resetCredentials( request, response )
        self.failUnless( response._unauthorized_called )
