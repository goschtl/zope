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
"""Generic PAS Plugins

$Id$
"""
__docformat__ = "reStructuredText"
from persistent import Persistent
from zope.interface import implements

from zope.app.container.contained import Contained
from zope.app.security.interfaces import IUnauthenticatedPrincipal

from interfaces import IChallengePlugin


class AlreadyAuthenticatedUserChallenger(Persistent, Contained):
    """Authenticated User Challenger

    Create no challenge, if the user is already authenticated.

    >>> challenger = AlreadyAuthenticatedUserChallenger()

    >>> from zope.publisher.browser import TestRequest
    >>> request = TestRequest()
    >>> response = request.response

    >>> challenger.challenge(request, response)
    True

    >>> class Principal(object):
    ...     implements(IUnauthenticatedPrincipal)
    >>> request._principal = Principal()

    >>> challenger.challenge(request, response) is None
    True
    """
    implements(IChallengePlugin)

    def challenge(self, request, response):
        if not IUnauthenticatedPrincipal.providedBy(request.principal):
            return True

        return None
