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
"""Unautorized Exception View Class

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.app import zapi
from zope.app.security.interfaces import IAuthenticationService


class Unauthorized(object):

    def issueChallenge(self):
        # Set the error status to 403 (Forbidden) in the case when we don't
        # challenge the user
        self.request.response.setStatus(403)
        principal = self.request.principal
        auth = zapi.getService(zapi.servicenames.Authentication)
        auth.unauthorized(principal.id, self.request)
