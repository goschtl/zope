##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
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

from zope.proxy import removeAllProxies
from zope.publisher.interfaces.http import MethodNotAllowed

from zope.pipeline.envkeys import REQUEST_KEY
from zope.pipeline.envkeys import TRAVERSED_KEY


class Caller(object):
    """WSGI app that calls the traversed object.

    Requires 'zope.pipeline.request' and 'zope.pipeline.traversed' in
    the environment.
    """

    def get_target(self, environ):
        """Returns the object to call."""
        traversed = environ[TRAVERSED_KEY]
        name, ob = traversed[-1]
        return ob

    def __call__(self, environ, start_response):
        ob = self.get_target(environ)
        request = environ[REQUEST_KEY]
        positional = request.getPositionalArguments()
        result = mapply(ob, positional, request)
        response = request.response
        if result is not response:
            response.setResult(result)
        start_response(response.getStatusString(), response.getHeaders())
        return response.consumeBodyIter()

    def __repr__(self):
        return '%s()' % self.__class__.__name__


class HTTPCaller(Caller):
    """Caller for HTTP: Returns an empty body for HEAD requests.

    Other request methods 
    """
    implements(IWSGIApplication)

    def __call__(self, environ, start_response):
        res = super(HTTPCaller, self)(environ, start_response)
        if request.method == 'HEAD':
            # Send the headers, but discard the body.
            # Note that a HEAD request can have a nonzero Content-Length
            # header, while the body has zero length.  This seems to follow
            # the HTTP spec.
            if hasattr(res, 'close'):
                res.close()
            res = ('',)
        return res


class HTTPRequestMethodCaller(HTTPCaller):
    """Caller for HTTP: calls the view and method specified by REQUEST_METHOD.

    This is normally used for non-browser requests such as PUT, DELETE, etc.
    """

    def get_target(self, environ):
        """Returns the object to call."""
        orig = super(HTTPRequestMethodCaller, self).get_target(environ)

        # The commented code below matches the behavior of
        # zope.app.publication, but that behavior is strange and
        # undocumented.  If anyone needs this code, please explain
        # why.

        #if IHTTPException.providedBy(orig):
        #    return orig

        request = environ[REQUEST_KEY]
        # Get the view named by the request method
        ob = queryMultiAdapter((orig, request), name=request.method)
        # Get the method of that view with the same name
        ob = getattr(ob, request.method, None)
        if ob is None:
            raise MethodNotAllowed(orig, request)
        return ob


_marker = object()  # Create a new marker object.

def unwrapMethod(obj):
    """obj -> (unwrapped, wrapperCount)

    Unwrap 'obj' until we get to a real function, counting the number of
    unwrappings.

    Bail if we find a class or something we can't identify as callable.
    """
    wrapperCount = 0
    unwrapped = obj

    for i in range(10):
        bases = getattr(unwrapped, '__bases__', None)
        if bases is not None:
            raise TypeError("mapply() can not call class constructors")

        im_func = getattr(unwrapped, 'im_func', None)
        if im_func is not None:
            unwrapped = im_func
            wrapperCount += 1
        elif getattr(unwrapped, 'func_code', None) is not None:
            break
        else:
            unwrapped = getattr(unwrapped, '__call__' , None)
            if unwrapped is None:
                raise TypeError("mapply() can not call %s" % repr(obj))
    else:
        raise TypeError("couldn't find callable metadata, mapply() error on %s"
                        % repr(obj))

    return unwrapped, wrapperCount


def mapply(obj, positional=(), request={}):
    __traceback_info__ = obj

    # we need deep access for introspection. Waaa.
    unwrapped = removeAllProxies(obj)

    unwrapped, wrapperCount = unwrapMethod(unwrapped)

    code = unwrapped.func_code
    defaults = unwrapped.func_defaults
    names = code.co_varnames[wrapperCount:code.co_argcount]

    nargs = len(names)
    if not positional:
        args = []
    else:
        args = list(positional)
        if len(args) > nargs:
            given = len(args)
            if wrapperCount:
                given += wrapperCount
            raise TypeError('%s() takes at most %d argument%s(%d given)' % (
                getattr(unwrapped, '__name__', repr(obj)),
                code.co_argcount,
                (code.co_argcount > 1 and 's ' or ' '),
                given))

    get = request.get
    nrequired = len(names)
    if defaults:
        nrequired -= len(defaults)

    for index in range(len(args), nargs):
        name = names[index]
        v = get(name, _marker)
        if v is _marker:
            if name == 'REQUEST':
                v = request
            elif index < nrequired:
                raise TypeError('Missing argument to %s(): %s' % (
                    getattr(unwrapped, '__name__', repr(obj)), name))
            else:
                v = defaults[index - nrequired]
        args.append(v)

    args = tuple(args)

    if __debug__:
        return debug_call(obj, args)

    return obj(*args)

def debug_call(obj, args):
    # The presence of this function allows us to set a pdb breakpoint
    return obj(*args)
