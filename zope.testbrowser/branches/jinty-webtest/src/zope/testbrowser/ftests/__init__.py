##############################################################################
#
# Copyright (c) Zope Corporation and Contributors.
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

class View:

    def __init__(self, context, request):
        self.context = context
        self.request = request

_interesting_environ = ('CONTENT_LENGTH',
                        'CONTENT_TYPE',
                        'HTTP_ACCEPT_LANGUAGE',
                        'HTTP_CONNECTION',
                        'HTTP_HOST',
                        'HTTP_USER_AGENT',
                        'PATH_INFO',
                        'REQUEST_METHOD')

class Echo(View):
    """Simply echo the interesting parts of the request"""

    def __call__(self):
        items = []
        for k in _interesting_environ:
            v = self.request.get(k, None)
            if v is None:
                continue
            items.append('%s: %s' % (k, v))
        items.extend('%s: %s' % x for x in sorted(self.request.form.items())) 
        items.append('Body: %r' % self.request.bodyStream.read())
        return '\n'.join(items)

class GetCookie(View):
    """Gets cookie value"""

    def __call__(self):
        return '\n'.join(
            ('%s: %s' % (k, v)) for k, v in sorted(
                self.request.cookies.items()))

class SetCookie(View):
    """Sets cookie value"""

    def __call__(self):
        self.request.response.setCookie(
            **dict((str(k), str(v)) for k, v in self.request.form.items()))


class SetStatus(View):
    """Sets HTTP status"""

    def __call__(self):
        status = self.request.get('status')
        if status:
            self.request.response.setStatus(int(status))
            return 'Just set a status of %s' % status
        else:
            return 'Everything fine'
