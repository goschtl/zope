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
"""Base implementations of the Publisher objects

Specifically, 'BaseRequest', 'BaseResponse', and 'DefaultPublication' are
specified here.

$Id: base.py,v 1.14 2004/02/16 21:37:19 srichter Exp $
"""
import traceback
from cStringIO import StringIO

from zope.interface import implements
from zope.interface.common.mapping import IReadMapping, IEnumerableMapping
from zope.exceptions import NotFoundError

from zope.publisher.interfaces import IPublication
from zope.publisher.interfaces import NotFound, DebugError, Unauthorized
from zope.publisher.interfaces import IRequest, IResponse
from zope.publisher.publish import mapply

_marker = object()

class BaseResponse(object):
    """Base Response Class
    """

    __slots__ = (
        '_body',      # The response body
        '_outstream', # The output stream
        )

    implements(IResponse)


    def __init__(self, outstream):
        self._body = ''
        self._outstream = outstream

    def outputBody(self):
        'See IPublisherResponse'
        self._outstream.write(self._getBody())

    def setBody(self, body):
        'See IPublisherResponse'
        self._body = body

    # This method is not part of this interface
    def _getBody(self):
        'Returns a string representing the currently set body.'
        return self._body

    def reset(self):
        'See IPublisherResponse'
        self._body = ""

    def handleException(self, exc_info):
        'See IPublisherResponse'
        traceback.print_exception(
            exc_info[0], exc_info[1], exc_info[2], 100, self)

    def internalError(self):
        'See IPublisherResponse'
        pass

    def retry(self):
        'See IPublisherResponse'
        return self.__class__(self.outstream)

    def write(self, string):
        'See IApplicationResponse'
        self._body += string

class RequestDataGetter(object):

    implements(IReadMapping)

    def __init__(self, request):
        self.__get = getattr(request, self._gettrname)

    def __getitem__(self, name):
        return self.__get(name)

    def get(self, name, default=None):
        return self.__get(name, default)

    def __contains__(self, key):
        lookup = self.get(key, self)
        return lookup is not self

    has_key = __contains__

class RequestDataMapper(object):

    implements(IEnumerableMapping)

    def __init__(self, request):
        self.__map = getattr(request, self._mapname)

    def __getitem__(self, name):
        return self.__map[name]

    def get(self, name, default=None):
        return self.__map.get(name, default)

    def __contains__(self, key):
        lookup = self.get(key, self)
        return lookup is not self

    has_key = __contains__

    def keys(self):
        return self.__map.keys()

    def __iter__(self):
        return iter(self.keys())

    def items(self):
        return self.__map.items()

    def values(self):
        return self.__map.values()

    def __len__(self):
        return len(self.__map)

class RequestDataProperty(object):

    def __init__(self, gettr_class):
        self.__gettr_class = gettr_class

    def __get__(self, request, rclass=None):
        if request is not None:
            return self.__gettr_class(request)

    def __set__(*args):
        raise AttributeError, 'Unassignable attribute'


class RequestEnvironment(RequestDataMapper):
    _mapname = '_environ'

class BaseRequest(object):
    """Represents a publishing request.

    This object provides access to request data. Request data may
    vary depending on the protocol used.

    Request objects are created by the object publisher and will be
    passed to published objects through the argument name, REQUEST.

    The request object is a mapping object that represents a
    collection of variable to value mappings.
    """

    implements(IRequest)

    __slots__ = (
        '_held',             # Objects held until the request is closed
        '_traversed_names',  # The names that have been traversed
        '_last_obj_traversed', # Object that was traversed last
        '_traversal_stack',  # Names to be traversed, in reverse order
        '_environ',          # The request environment variables
        '_response',         # The response
        '_args',             # positional arguments
        '_body_instream',    # input stream
        '_body',             # The request body as a string
        '_publication',      # publication object
        '_presentation_skin', # View skin
        '_user'               # request user, set by publication
        )

    environment = RequestDataProperty(RequestEnvironment)

    def __init__(self, body_instream, outstream, environ, response=None,
                 positional=()):
        self._traversal_stack = []
        self._last_obj_traversed = None
        self._traversed_names = []
        self._environ = environ

        self._args = positional
        if response is None:
            self._response = self._createResponse(outstream)
        else:
            self._response = response
        self._body_instream = body_instream
        self._held = ()
        self._user = None

    def setUser(self, user):
        self._user = user

    user = property(lambda self: self._user)

    def _getPublication(self):
        'See IPublisherRequest'
        return getattr(self, '_publication', None)

    publication = property(_getPublication)


    def processInputs(self):
        'See IPublisherRequest'
        # Nothing to do here

    def retry(self):
        'See IPublisherRequest'
        raise TypeError('Retry is not supported')

    def setPublication(self, pub):
        'See IPublisherRequest'
        self._publication = pub

    def supportsRetry(self):
        'See IPublisherRequest'
        return 0

    def traverse(self, object):
        'See IPublisherRequest'

        publication = self.publication

        traversal_stack = self._traversal_stack
        traversed_names = self._traversed_names

        self._last_obj_traversed = object

        prev_object = None
        while 1:

            if object is not prev_object:
                # Invoke hooks (but not more than once).
                publication.callTraversalHooks(self, object)

            prev_object = object

            if traversal_stack:
                # Traverse to the next step.
                entry_name = traversal_stack.pop()
                traversed_names.append(entry_name)
                subobject = publication.traverseName(
                    self, object, entry_name)
                self._last_obj_traversed = object = subobject
            else:
                # Finished traversal.
                break

        return object

    def close(self):
        'See IPublicationRequest'
        self._held = None
        self._response = None
        self._body_instream = None
        self._publication = None

    def getPositionalArguments(self):
        'See IPublicationRequest'
        return self._args

    def _getResponse(self):
        return self._response

    response = property(_getResponse)

    def getTraversalStack(self):
        'See IPublicationRequest'
        return list(self._traversal_stack) # Return a copy

    def hold(self, object):
        'See IPublicationRequest'
        self._held = self._held + (object,)

    def setTraversalStack(self, stack):
        'See IPublicationRequest'
        self._traversal_stack[:] = list(stack)

    def setPresentationSkin(self, skin):
        'See IPublicationRequest'
        self._presentation_skin = skin

    def getPresentationSkin(self):
        'See IPresentationRequest'
        return getattr(self, '_presentation_skin', '')

    def _getBody(self):
        body = getattr(self, '_body', None)
        if body is None:
            s = self._body_instream
            if s is None:
                return None # XXX what should be returned here?
            p = s.tell()
            s.seek(0)
            body = s.read()
            s.seek(p)
            self._body = body
        return body

    body = property(_getBody)

    def _getBodyFile(self):
        'See IApplicationRequest'
        return self._body_instream

    bodyFile = property(_getBodyFile)

    def __len__(self):
        'See Interface.Common.Mapping.IEnumerableMapping'
        return len(self.keys())

    def items(self):
        'See Interface.Common.Mapping.IEnumerableMapping'
        result = []
        get = self.get
        for k in self.keys():
            result.append((k, get(k)))
        return result

    def keys(self):
        'See Interface.Common.Mapping.IEnumerableMapping'
        return self._environ.keys()

    def __iter__(self):
        return iter(self.keys())

    def values(self):
        'See Interface.Common.Mapping.IEnumerableMapping'
        result = []
        get = self.get
        for k in self.keys():
            result.append(get(k))
        return result

    def __getitem__(self, key):
        'See Interface.Common.Mapping.IReadMapping'
        result = self.get(key, _marker)
        if result is _marker:
            raise KeyError, key
        else:
            return result

    def get(self, key, default=None):
        'See Interface.Common.Mapping.IReadMapping'

        result = self._environ.get(key, self)
        if result is not self: return result

        return default

    def __contains__(self, key):
        'See Interface.Common.Mapping.IReadMapping'
        lookup = self.get(key, self)
        return lookup is not self

    has_key = __contains__

    def _createResponse(self, outstream):
        # Should be overridden by subclasses
        return BaseResponse(outstream)

    def __nonzero__(self):
        # This is here to avoid calling __len__ for boolean tests
        return 1

    def __str__(self):
        L1 = self.items()
        L1.sort()
        return "\n".join(map(lambda item: "%s:\t%s" % item, L1))

    def _setupPath_helper(self, attr):
        path = self.get(attr, "/").strip()
        if path.endswith('/'):
            path = path[:-1] # XXX Why? Not sure
            self._endswithslash = 1
        else:
            self._endswithslash = 0

        clean = []
        for item in path.split('/'):
            if not item or item == '.':
                continue
            elif item == '..':
                try: del clean[-1]
                except IndexError:
                    raise NotFoundError('..')
            else: clean.append(item)

        clean.reverse()
        self.setTraversalStack(clean)

        self._path_suffix = None

class TestRequest(BaseRequest):

    __slots__ = ('_presentation_type', )

    def __init__(self, path, body_instream=None, outstream=None, environ=None):
        if environ is None:
            environ = {}
        environ['PATH_INFO'] = path
        if body_instream is None:
            body_instream = StringIO('')
        if outstream is None:
            outstream = StringIO()

        super(TestRequest, self).__init__(body_instream, outstream, environ)


class DefaultPublication:

    implements(IPublication)

    require_docstrings = 1

    def __init__(self, app):
        self.app = app

    def beforeTraversal(self, request):
        # Lop off leading and trailing empty names
        stack = request.getTraversalStack()
        while stack and not stack[-1]:
            stack.pop() # toss a trailing empty name
        while stack and not stack[0]:
            stack.pop(0) # toss a leading empty name
        request.setTraversalStack(stack)

    def getApplication(self, request):
        return self.app

    def callTraversalHooks(self, request, ob):
        pass

    def traverseName(self, request, ob, name, check_auth=1):
        if name.startswith('_'):
            raise Unauthorized("Name %s begins with an underscore" % `name`)
        if hasattr(ob, name):
            subob = getattr(ob, name)
        else:
            try:
                subob = ob[name]
            except (KeyError, IndexError,
                    TypeError, AttributeError):
                raise NotFound(ob, name, request)
        if self.require_docstrings and not getattr(subob, '__doc__', None):
            raise DebugError(subob, 'Missing or empty doc string')
        return subob

    def getDefaultTraversal(self, request, ob):
        return ob, ()

    def afterTraversal(self, request, ob):
        pass

    def callObject(self, request, ob):
        return mapply(ob, request.getPositionalArguments(), request)

    def afterCall(self, request):
        pass

    def handleException(self, object, request, exc_info, retry_allowed=1):
        # Let the response handle it as best it can.
        request.response.reset()
        request.response.handleException(exc_info)


class TestPublication(DefaultPublication):

    def traverseName(self, request, ob, name, check_auth=1):
        if hasattr(ob, name):
            subob = getattr(ob, name)
        else:
            try:
                subob = ob[name]
            except (KeyError, IndexError,
                    TypeError, AttributeError):
                raise NotFound(ob, name, request)
        return subob
