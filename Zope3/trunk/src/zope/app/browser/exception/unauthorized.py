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

$Id: unauthorized.py,v 1.1 2003/02/05 11:34:53 stevea Exp $
"""
__metaclass__ = type
import sys
from zope.exceptions.exceptionformatter import format_exception
from zope.app.traversing import getParent
from zope.app.interfaces.security import IAuthenticationService

class Unauthorized:

    def __init__(self, context, request):
        self.context = context
        self.request = request

        t, v, tb = sys.exc_info()
        try:
            self.traceback = ''.join(format_exception(t, v, tb, as_html=1))
        finally:
            tb = None

    def issueChallenge(self):
        principal = self.request.user
        prinreg = getParent(principal)
        assert IAuthenticationService.isImplementedBy(prinreg)
        prinreg.unauthorized(principal.getId(), self.request)

