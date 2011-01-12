##############################################################################
#
# Copyright (c) 2011 Zope Foundation and Contributors.
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
from __future__ import absolute_import

try:
    import simplejson as json
except ImportError:
    import json

import webob
import zc.dozodb


def response(handler, request):
    try:
        if request.method == 'GET':
            if '_p_oid' in request.str_GET:
                return zc.dozodb.load(
                    handler.connection, request.str_GET.get('_p_oid'))
            body = zc.dozodb.fetched(*handler.query())
        else:
            assert(request.method == 'POST')
            assert request.content_type.startswith('application/json')
            body = zc.dozodb.save(handler, request.body)
    except Exception, e:
        body = json.dumps(dict(error=unicode(e)))

    response = webob.Response(status = 200, content_type = 'application/json')
    response.body = body
    return response

class Application:

    def __init__(self, handler, db):
        self.db = db
        self.handler = handler

    def __call__(self, environment, start_response):
        request = webob.Request(environment)
        with self.db.transaction() as connection:
            r = response(self.handler(connection, request), request)
            return r(environment, start_response)

