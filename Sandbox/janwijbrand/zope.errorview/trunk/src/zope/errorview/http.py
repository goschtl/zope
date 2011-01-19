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
"""Unauthorized Exception

$Id: unauthorized.py 100273 2009-05-23 02:20:25Z shane $
"""

from zope.interface import implements
from zope.publisher.interfaces.http import IHTTPException
from zope.browser.interfaces import ISystemErrorView
from zope.component import getAdapters
from zope.interface import Interface

class SystemErrorViewMixin:

    implements(ISystemErrorView)

    def isSystemError(self):
        return True

class ExceptionViewBase(object):

    implements(IHTTPException)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.response = request.response

    def __call__(self):
        self.response.setStatus(500)
        return ''

    def __str__(self):
        return self()

class ExceptionView(ExceptionViewBase, SystemErrorViewMixin):
    pass

class TraversalExceptionView(ExceptionViewBase):

    def __call__(self):
        if self.request.method =='MKCOL' and self.request.getTraversalStack():
            # MKCOL with non-existing parent.
            self.request.response.setStatus(409)
        else:
            self.request.response.setStatus(404)
        return ''

class UnauthorizedView(ExceptionViewBase):

    def __call__(self):
        self.request.unauthorized('basic realm="Zope"')
        self.request.response.setStatus(401)
        return ''

class MethodNotAllowedView(ExceptionViewBase):

    def allowed(self):
        # XXX how to determine the allowed HTTP methods?  XXX we need
        # a safe way to determine the allow HTTP methods. Or should we
        # let the application handle it?
        return []

    def __call__(self):
        error = self.context
        allow = self.allowed()
        self.request.response.setStatus(405)
        self.request.response.setHeader('Allow', ', '.join(allow))
        return ''

