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
"""Unautorized Exception View Class

$Id: unauthorized.py,v 1.6 2003/08/12 19:14:53 srichter Exp $
"""
from zope.app.traversing import getParent
from zope.app.interfaces.security import IAuthenticationService

__metaclass__ = type


class Unauthorized:

    def issueChallenge(self):
        # Set the error status to 403 (Forbidden) in the case when we don't
        # challenge the user
        self.request.response.setStatus(403)
        principal = self.request.user
        prinreg = getParent(principal)
        if not IAuthenticationService.isImplementedBy(prinreg):
            # With PluggableAuthenticationService, principals are
            # contained in the PrincipalSource, which is contained in
            # the service.
            prinreg = getParent(prinreg)
        assert IAuthenticationService.isImplementedBy(prinreg)
        prinreg.unauthorized(principal.getId(), self.request)
