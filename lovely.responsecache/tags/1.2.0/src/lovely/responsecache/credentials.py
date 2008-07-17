##############################################################################
#
# Copyright (c) 2006-2007 Lovely Systems and Contributors.
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
"""
$Id$
"""
__docformat__ = "reStructuredText"

from zope import component

from zope.publisher.interfaces.http import IHTTPRequest
from zope.app.session.interfaces import IClientIdManager, ISession

from zope.app.authentication.session import (
        SessionCredentialsPlugin,
        SessionCredentials,
        )


class CredentialsPlugIn(SessionCredentialsPlugin):
    """A credentials plugin which makes sure that the session id is user
    dependent.
    """

    def extractCredentials(self, request):
        if not IHTTPRequest.providedBy(request):
            return None
        # first we check if there is a login in the request
        login = request.get(self.loginfield, None)
        password = request.get(self.passwordfield, None)
        credentials = None
        if login and password:
            # there is a login in the request, create the credentials from the
            # request
            credentials = SessionCredentials(login, password)
        session = ISession(request, None)
        sessionData = session.get(
            'zope.app.authentication.browserplugins')
        if credentials is None and not sessionData:
            return None
        sessionData = session[
            'zope.app.authentication.browserplugins']
        sessionCredentials = sessionData.get('credentials', None)
        if credentials:
            if (   sessionCredentials is None
                or sessionCredentials.getLogin() != credentials.getLogin()
               ):
                # we need a new client id and a new session to make the
                # session id user specific
                manager = component.getUtility(IClientIdManager)
                id = manager.generateUniqueId()
                manager.setRequestId(request, id)
                session = ISession(request, None)
                sessionData = session.get(
                    'zope.app.authentication.browserplugins')
                sessionData = session[
                    'zope.app.authentication.browserplugins']
            sessionData['credentials'] = credentials
        else:
            credentials = sessionData.get('credentials', None)
        if not credentials:
            return None
        return {'login': credentials.getLogin(),
                'password': credentials.getPassword()}

