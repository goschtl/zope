##############################################################################
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
##############################################################################
"""
$Id: __init__.py,v 1.1 2004/01/30 22:20:53 sidnei Exp $
"""

from zope.app import zapi
from zope.app.publisher.browser import BrowserView
from zope.app.interfaces.file import IReadFile, IWriteFile
from zope.app.content import queryContentType

class ExternalEditor(BrowserView):

    def __call__(self):
        context = self.context
        request = self.request
        response = request.response

        r = []
        url = zapi.getView(context, 'absolute_url', request)()
        r.append('url:%s' % url)
        adapted = zapi.getAdapter(context, IReadFile)

        r.append('content_type:%s' % adapted.contentType)

        # XXX There's no such thing as a meta_type
        # in Zope3, so we try to get as far as we can
        # using IContentType, which is a marker interface
        meta_type = queryContentType(context)
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
