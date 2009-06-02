##############################################################################
#
# Copyright Zope Foundation and Contributors.
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

import bobo
import zope.event
import zope.i18n.interfaces
import zope.publisher.browser
import zope.publisher.http
import webob
import webob.multidict

class BozoMultiDict:

    def __init__(self, data):
        self.data = data

    def __getitem__(self, k):
        v = self.data[k]
        if isinstance(v, list):
            return v[-1]
        return v

    def getall(self, name):
        value = self.data.get(name)
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    def getone(self, name):
        value = self.data.get(name)
        if value is None:
            raise KeyError(name)
        if isinstance(value, list):
            if len(value) != 1:
                raise KeyError(name)
            value = value[0]
        return value

    def mixed(self):
        return self.data

    def dict_of_lists(self):
        return dict((k, self.getall(k)) for k in self.data)

    def __contains__(self, k):
        return k in self.data

    def copy(self):
        return self.__class__(self.data.copy())

    def __len__(self):
        return len(self.data)

    def iteritems(self):
        data = self.data
        for k in sorted(data):
            v = data[k]
            if isinstance(v, list):
                for x in v:
                    yield k, x
            else:
                yield k, v

    def items(self):
        return list(self.iteritems())

    def iterkeys(self):
        return (item[0] for item in self.iteritems())

    __iter__ = iterkeys

    def keys(self):
        return list(self.iterkeys())

    def itervalues(self):
        return (item[1] for item in self.iteritems())

    def values(self):
        return list(self.itervalues())

    def __repr__(self):
        return "BozoMultiDict(%r)" % self.items()

class Request(zope.publisher.browser.BrowserRequest):

    __slots__ = ('_webob', '_form', '_charsets')

    def __init__(self, *args):
        zope.publisher.browser.BrowserRequest.__init__(self, *args)
        self.processInputs()

    @classmethod
    def blank(class_, *args, **kw):
        environ = webob.Request.blank(*args, **kw).environ
        return class_(environ['wsgi.input'], environ)

    @property
    def charsets(self):
        try:
            return self._charsets
        except AttributeError:
            pass

        adapter = zope.i18n.interfaces.IUserPreferredCharsets(self, None)
        if adapter is None:
            adapter = zope.publisher.http.HTTPCharsets(self)

        self._charsets = adapter.getPreferredCharsets() or ['utf-8']

        return self._charsets

    @property
    def charset(self):
        return self.charsets[0]

    @property
    def environ(self):
        return self._environ

    @property
    def webob(self):
        try:
            return self._webob
        except AttributeError:
            w = self._webob = webob.Request(self._environ)
            if w.charset is None:
                w.charset = self.charset
            return w

    @property
    def headers(self):
        return self.webob.headers

    def __getattr__(self, name):
        if name == '_webob':
            raise AttributeError(name)
        return getattr(self.webob, name)

    def __setattr__(self, name, value):
        try:
            object.__setattr__(self, name, value)
        except AttributeError:
            if name == 'charsets':
                if value is None:
                    return
                raise
            setattr(self.webob, name, value)

    def __delattr__(self, name):
        try:
            object.__delattr__(self, name)
        except AttributeError:
            delattr(self.webob, name)

    @property
    def body_file(self):
        return self.bodyStream

    @property
    def body(self):
        stream = self.bodyStream
        stream.seek(0)
        return stream.read()

    @property
    def params(self):
        return BozoMultiDict(self.form)

    @property
    def params(self):
        return BozoMultiDict(self.form)

    GET = params

    @property
    def POST(self):
        if self.method in ('POST', 'PUT'):
            content_type = self._environ.get('CONTENT_TYPE')
            if content_type and (
                content_type.startswith('application/x-www-form-urlencoded')
                or
                content_type.startswith('multipart/')
                ):
                return self.params
        return webob.multidict.NoVars('Not a POST request')


class Application(bobo.Application):

    def __call__(self, environ, start_response):
        request = Request(environ['wsgi.input'], environ)
        zope.event.notify(BeginRequest(request))
        try:
            return self.bobo_response(
                request, request.path_info, request.method
                )(environ, start_response)
        finally:
            zope.event.notify(EndRequest(request))

    def build_response(self, request, method, data):
        content_type = data.content_type
        response = request.response
        if content_type:
            response.setHeader('Content-Type', content_type)
        for name, value in data.headers:
            response.setHeader(name, value)
        result = data.body
        if result is not response:
            response.setResult(result)

        def wsgiresponse(environ, start_response):
            start_response(response.getStatusString(), response.getHeaders())
            return response.consumeBodyIter()

        return wsgiresponse

class RequestEvent:
    def __init__(self, request):
        self.request = request

class BeginRequest(RequestEvent):
    "A request has begun"

class EndRequest(RequestEvent):
    "A request has finished processing"
