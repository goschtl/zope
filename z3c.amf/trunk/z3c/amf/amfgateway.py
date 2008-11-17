# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""
$Id$
"""

import logging
import sys
import traceback
import types

from z3c.amf.interfaces import IAMFResponse
from zExceptions import Unauthorized, NotFound
from zope.interface import implements

import pyamf
from pyamf import remoting
from pyamf.remoting import amf0


class AMFParser(object):
    """
    Parse the request
    """

    def __init__(self, data):
        context = pyamf.get_context(pyamf.AMF0)
        self.requests = remoting.decode(data, context)
        self.auth = None

    def parse(self):
        name, request = self.requests.items()[0]
        if self.requests.headers:
            self.auth = self.requests.headers.get(u'Credentials')
        self.method = request.target
        params = request.body
        if params[0] is None:
            self.args = tuple()
        else:
            self.args = tuple(params)
        self.amfVersion = self.requests.amfVersion
        self.clientType = self.requests.clientType
        self.name = name


def parse_input(data):
    parser = AMFParser(data)
    return parser.parse()


class AMFResponse:
    """Customized Response that handles AMF-specific details.

    We override setBody to marhsall Python objects into AMF. We
    also override exception to convert errors to AMF faults.
    """
    implements(IAMFResponse)
    _contentType = remoting.CONTENT_TYPE

    # Because we can't predict what kind of thing we're customizing,
    # we have to use delegation, rather than inheritence to do the
    # customization.

    def __init__(self, real):
        self.__dict__['_real']=real

    def __getattr__(self, name):
        return getattr(self._real, name)

    def __setattr__(self, name, v):
        return setattr(self._real, name, v)

    def __delattr__(self, name):
        return delattr(self._real, name)

    def setBody(self, body, title='', is_error=0, bogus_str_search=None):
        responseBody = remoting.Envelope(self._amfVersion,
                                         self._clientType)
        context = pyamf.get_context(pyamf.AMF0)
        proc = amf0.RequestProcessor(self)
        if isinstance(body, remoting.BaseFault):
            amfResponse = remoting.Response(body,
                                            status=remoting.STATUS_ERROR)
        else:
            amfResponse = remoting.Response(body)
        responseBody[self._name] = amfResponse
        body = remoting.encode(responseBody, context)
        body.seek(0)
        self._real.setBody(body.read())
        self._setHeader()
        return self

    def exception(self, fatal=0, info=None,
                  absuri_match=None, tag_search=None):
        if isinstance(info, tuple) and len(info)==3:
            t, v, tb = info
        else:
            t, v, tb = sys.exc_info()

        content = "".join(traceback.format_tb(tb))
        logger = logging.getLogger('Zope')
        logger.info('AMF Exception: %s' % content)
        f=None
        self._real.setStatus(200)
        if t == 'Unauthorized' or t == Unauthorized or (
           isinstance(t, types.ClassType) and issubclass(t, Unauthorized)):
            # 401
            f = remoting.ErrorFault(code=str(t), type='Not authorized')
        elif isinstance(v, NotFound): # 404
            f = remoting.ErrorFault(code='NotFound',
                                    type='Resource not found',
                                    description=str(v))
        elif not isinstance(v, pyamf.BaseError): # 500
            f = remoting.ErrorFault(code=str(t), type=str(v), description=content)
        self.setBody(f)
        return tb

    def _setHeader(self):
        self.setHeader('content-length', len(self._real.body))
        self._real.setHeader('content-type', self._contentType)
