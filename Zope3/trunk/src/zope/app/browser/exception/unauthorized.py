##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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

$Id: unauthorized.py,v 1.4 2003/03/24 10:42:09 ryzaja Exp $
"""
__metaclass__ = type
from zope.app.traversing import getParent
from zope.app.interfaces.security import IAuthenticationService

class Unauthorized:

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def issueChallenge(self):
        # Set the error status to 403 (Forbidden) in the case when we don't
        # challenge the user
        self.request.response.setStatus(403)
        principal = self.request.user
        prinreg = getParent(principal)
        assert IAuthenticationService.isImplementedBy(prinreg)
        prinreg.unauthorized(principal.getId(), self.request)
