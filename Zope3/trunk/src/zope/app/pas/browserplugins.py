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
""" Implementations of the session-based and cookie-based extractor and
    challenge plugins.

$Id$
"""

import zope.interface
from zope.app.session.interfaces import ISession
from zope.app.pas import interfaces

class SessionExtractor:
    """ session-based credential extractor
    """
    zope.interface.implements(interfaces.IExtractionPlugin)

    def extractCredentials(self, request):
        """ Extract the credentials that are referenced in the
            request by looking them up in the session.

            >>> from zope.app.session.session import RAMSessionDataContainer
            >>> from zope.app.session.session import Session
            >>> from tests import sessionSetUp
            >>> request = sessionSetUp(RAMSessionDataContainer)
            >>> sessionData = Session(request)['pas_credentials']
            >>> sessionData['username'] = 'scott'
            >>> sessionData['password'] = 'tiger'

            >>> se = SessionExtractor()
            >>> se.extractCredentials(request)
            {'username': 'scott', 'password': 'tiger'}
        """
        sessionData = ISession(request)['pas_credentials']
        return {'username': sessionData['username'],
                'password': sessionData['password']}


