##############################################################################
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
##############################################################################
"""
$Id$
"""

from zope.app import zapi
from zope.app.publisher.browser import BrowserView
from zope.app.filerepresentation.interfaces import IReadFile, IWriteFile
from zope.app.interface import queryType
from zope.app.content.interfaces import IContentType
from zope.security.proxy import trustedRemoveSecurityProxy

class ExternalEditor(BrowserView):

    def __call__(self):
        context = self.context
        request = self.request
        response = request.response

        r = []
        url = zapi.getView(context, 'absolute_url', request)()
        r.append('url:%s' % url)
        adapted = IReadFile(context)

        if hasattr(adapted, 'contentType'):
            # XXX Although IReadFile declares contentType,
            # the default adapter for File doesn't seem
            # to provide it.
            r.append('content_type:%s' % adapted.contentType)

        # XXX There's no such thing as a meta_type
        # in Zope3, so we try to get as far as we can
        # using IContentType, which is a marker interface
        # XXX Had to use trustedRemoveSecurityProxy because
        # I was getting I was getting unauthorized on __iro__
        meta_type = queryType(trustedRemoveSecurityProxy(context), IContentType)
        if meta_type:
            r.append('meta_type:%s' % meta_type.__name__)

        auth = request._auth

        if auth is not None:
            if auth.endswith('\n'):
                auth = auth[:-1]
            r.append('auth:%s' % auth)

        r.append('cookie:%s' % request._environ.get('HTTP_COOKIE', ''))

        # XXX Once we have lock, add the lock token here

        r.append('')

        response.setHeader('Pragma', 'no-cache')

        r.append(adapted.read())

        response.setHeader('Content-Type', 'application/x-zope-edit')
        return '\n'.join(r)
