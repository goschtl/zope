##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
# HTTP Basic Authentication adapter

from zope.publisher.interfaces.vfs import IVFSCredentials
from zope.app.security.loginpassword import LoginPassword

class BasicVFSAuthAdapter(LoginPassword):

    __used_for__ = IVFSCredentials

    __request = None

    def __init__(self, request):
        self.__request = request
        # XXX base64 decoding should be done here, not in request
        lpw = request._authUserPW()
        if lpw is None:
            login, password = None, None
        else:
            login, password = lpw
        LoginPassword.__init__(self, login, password)

    def needLogin(self, realm):
        self.__request.unauthorized("Did not work")
