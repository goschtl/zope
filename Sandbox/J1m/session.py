##############################################################################
#
# Copyright (c) 2005 Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

import sha

import zope.publisher.interfaces.http

import zope.app.authentication.session
import zope.session.interfaces
import zope.app.http.httpdate

class CredentialsDontMakeSecurityDeclarationsForMe:
    # Credentials class. We use this rather than a dict to prevent
    # leakage to untrusted code. As long as no one is fool enough to
    # make security declarations for this then untrusted code will get
    # forbidden errors trying to access data.

    domain = None
    
    def __init__(self, **kw):
        self.__dict__.update(kw)


class SessionCredentialsPlugin(
    zope.app.authentication.session.SessionCredentialsPlugin,
    ):

    _fields = ('login', 'login.login'), ('password', 'login.password')

    def extractCredentials(self, request):
        """Extracts credentials from a session if they exist."""

        if not zope.publisher.interfaces.http.IHTTPRequest.providedBy(request):
            return None

        data = dict((k, request[rk]) for (k, rk) in self._fields
                    if rk in request)
        credentials = None

        session = zope.session.interfaces.ISession(request)

        if len(data) == len(self._fields):
            data['sha'] = sha.new(data.pop('password').encode('utf-8')
                                  ).hexdigest()
            self.save_credentials(data, session)
            data['logging_in'] = True
            return self._update_cookie(request, data)

        sessionData = session.get('zope.app.authentication.browserplugins')
        if sessionData:
            return self._update_cookie(request,
                                       sessionData.get('credentials').__dict__)

        return None

    def _update_cookie(self, request, credentials):
        if credentials:
            domain = credentials.get('domain') 
            if domain and (request.cookies.get('login.domain') != domain):
                request.response.setCookie(
                    'login.domain', domain,
                    expires = 'Wed, 01-Jan-3000 00:00:00 GMT',
                    )
            credentials['request-annotations'] = request.annotations
            return credentials
    
    def save_credentials(self, credentials, session=None, request=None):
        if session is None:
            session = zope.session.interfaces.ISession(request)
        sessionData = session['zope.app.authentication.browserplugins']
        sessionData['credentials'] = (
            CredentialsDontMakeSecurityDeclarationsForMe(**credentials)
            )

    def logout(self, request):
        self.save_credentials({}, request=request)
        
    def challenge(self, request):
        if 'login.ignore' in request:
            return False
        return super(SessionCredentialsPlugin, self).challenge(request)

class DomainSessionCredentialsPlugin(SessionCredentialsPlugin):

    _fields = SessionCredentialsPlugin._fields + (('domain', 'login.domain'),)
