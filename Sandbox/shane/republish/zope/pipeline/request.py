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
"""Standard Zope request classes.
"""

from zope.interface import implements
from zope.publisher.interfaces import IDebugFlags
from zope.publisher.interfaces import IRequest
from zope.publisher.interfaces.http import IHTTPRequest

from zope.pipeline.response import BaseResponse


class DebugFlags(object):
    implements(IDebugFlags)

    sourceAnnotations = False
    showTAL = False


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
        '__provides__',      # Allow request to directly provide interfaces
        'environment',       # The request environment (CGI. WSGI, or similar)
        'bodyStream',        # body input stream
        'traversal_stack',   # Names to be traversed, in reverse order
        'traversal_hooks',   # list of functions to call during traversal
        'traversed',         # list of (name, obj) that have been traversed
        'traversed_default', # number of steps added by default traversal
        'principal',         # authorized principal
        'debug',             # debug flags
        'interaction',       # interaction, set by interaction
        'annotations',       # per-package annotations
        'response',          # The response
        'locale',            # The locale for the request
        )

    _response_factory = BaseResponse

    def __init__(self, environ):
        self.environment = environ
        self.bodyStream = environ.get('wsgi.input')
        self.traversal_stack = []
        self.traversal_hooks = []
        self.traversed = []
        self.traversed_default = 0
        self.principal = None
        self.debug = DebugFlags()
        self.interaction = None
        self.annotations = {}
        self.response = self._response_factory()
        self.locale = None

    def getTraversalStack(self):
        """Deprecated"""
        return self.traversal_stack

    def setTraversalStack(self, stack):
        """Deprecated"""
        self.traversal_stack[:] = list(stack)

    def setPrincipal(self, principal):
        """Deprecated"""
        self.principal = principal

    def getBasicCredentials(self):
        return None

    def _authUserPW(self):
        """Deprecated"""
        return self.getBasicCredentials()

    def unauthorized(self, challenge):
        """Deprecated"""
        self.response.unauthorized(challenge)

"""
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
            raise KeyError(key)
        else:
            return result

    def get(self, key, default=None):
        'See Interface.Common.Mapping.IReadMapping'
        result = self._environ.get(key, _marker)
        if result is not _marker:
            return result

        return default

    def __contains__(self, key):
        'See Interface.Common.Mapping.IReadMapping'
        lookup = self.get(key, self)
        return lookup is not self

    has_key = __contains__

    def __nonzero__(self):
        # This is here to avoid calling __len__ for boolean tests
        return 1

"""

    def __str__(self):
        items = self.items()
        items.sort()
        return "\n".join("%s:\t%s" % item for item in items)

"""
    def _setupPath_helper(self, attr):
        path = self.get(attr, "/")
        if path.endswith('/'):
            # Remove trailing backslash, so that we will not get an empty
            # last entry when splitting the path.
            path = path[:-1]
            self._endswithslash = True
        else:
            self._endswithslash = False

        clean = []
        for item in path.split('/'):
            if not item or item == '.':
                continue
            elif item == '..':
                try:
                    del clean[-1]
                except IndexError:
                    raise NotFound('..')
            else: clean.append(item)

        clean.reverse()
        self.setTraversalStack(clean)

        self._path_suffix = None
"""

class HTTPRequest(BaseRequest):
    implements(IHTTPRequest)

    __slots__ = (
        'method',         # The upper-cased request method (REQUEST_METHOD)
        '_cookies',       # The request cookies
        'form',
        'form_action',
        )
        #'_app_names',     # The application path as a sequence
        #'_app_server',    # The server path of the application url
        #'_endswithslash', # Does the given path end with /

    def __init__(self, environ):
        super(HTTPRequest, self).__init__(environ)
        self.method = environ.get("REQUEST_METHOD", 'GET').upper()
        
