##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""HTTP-specific interfaces and exceptions

$Id: browser.py 96546 2009-02-14 20:48:37Z shane $
"""

from zope.interface import Attribute
from zope.interface import implements
from zope.interface import Interface
from zope.publisher.interfaces.base import IPublishTraverse
from zope.publisher.interfaces.base import IRequest
from zope.publisher.interfaces.base import IResponse
from zope.publisher.interfaces.exceptions import IPublishingException
from zope.publisher.interfaces.exceptions import PublishingException


class IRedirect(IPublishingException):
    def getLocation():
        'Returns the location.'

class Redirect(PublishingException):

    implements(IRedirect)

    def __init__(self, location):
        self.location = location

    def getLocation(self):
        return self.location

    def __str__(self):
        return 'Location: %s' % self.location


class IMethodNotAllowed(IPublishingException):
    """An exception that signals the 405 Method Not Allowed HTTP error"""

    object = Attribute("""The object on which the error occurred""")

    request = Attribute("""The request in which the error occurred""")


class MethodNotAllowed(PublishingException):
    """An exception that signals the 405 Method Not Allowed HTTP error"""

    implements(IMethodNotAllowed)

    def __init__(self, object, request):
        self.object = object
        self.request = request

    def __str__(self):
        return "%r, %r" % (self.object, self.request)


class IHTTPRequest(IRequest):

    method = Attribute("Request method, normalized to upper case")

    def getCookies():
        """Return the cookie data

        Data are returned as a mapping object, mapping cookie name to value.
        """

    cookies = Attribute(
        """Request cookie data

        This is a read-only mapping from variable name to value.
        """)

    def getHeader(name, default=None, literal=False):
        """Get a header value

        Return the named HTTP header, or an optional default
        argument or None if the header is not found. Note that
        both original and CGI-ified header names are recognized,
        e.g. 'Content-Type', 'CONTENT_TYPE' and 'HTTP_CONTENT_TYPE'
        should all return the Content-Type header, if available.

        If the literal argument is passed, the header is searched
        'as is', eg: only if the case matches.
        """

    headers = Attribute(
        """Request header data

        This is a read-only mapping from variable name to value.
        It does *not* support iteration.
        """)

    URL = Attribute(
        """Request URL data

        When converted to a string, this gives the effective published URL.

        This object can also be used as a mapping object. The key must
        be an integer or a string that can be converted to an
        integer. A non-negative integer returns a URL n steps from the
        URL of the top-level application objects. A negative integer
        gives a URL that is -n steps back from the effective URL.

        For example, 'request.URL[-2]' is equivalent to the Zope 2
        'request["URL2"]'. The notion is that this would be used in
        path expressions, like 'request/URL/-2'.
        """)

    def getURL(level=0, path_only=False):
        """Return the published URL with level names removed from the end.

        If path_only is true, then only a path will be returned.
        """

    def getApplicationURL(depth=0, path_only=False):
        """Return the application URL plus depth steps

        If path_only is true, then only a path will be returned.
        """

    def getBasicAuth():
        """Return (login, password) if there are basic credentials.

        Return None if the request does not contain basic credentials.
        """

    def _authUserPw():
        """Deprecated: Use getBasicAuth() instead.
        """

    def unauthorized(challenge):
        """Issue a 401 Unauthorized error (asking for login/password).

        Sets the WWW-Authenticate header to the value of the
        challenge parameter.
        """


class IHTTPResponse(IResponse):
    """An object representation of an HTTP response."""

    def setHeader(name, value, literal=False):
        """Sets an HTTP return header "name" with value "value"

        The previous value is cleared. If the literal flag is true,
        the case of the header name is preserved, otherwise
        word-capitalization will be performed on the header name on
        output.
        """

    def addHeader(name, value):
        """Add an HTTP Header

        Sets a new HTTP return header with the given value, while retaining
        any previously set headers with the same name.
        """

    def getHeader(name, default=None):
        """Gets a header value

        Returns the value associated with a HTTP return header, or
        'default' if no such header has been set in the response
        yet.
        """

    def appendToCookie(name, value):
        """Append text to a cookie value

        If a value for the cookie has previously been set, the new
        value is appended to the old one separated by a colon.
        """

    def expireCookie(name, **kw):
        """Causes an HTTP cookie to be removed from the browser

        The response will include an HTTP header that will remove the cookie
        corresponding to "name" on the client, if one exists. This is
        accomplished by sending a new cookie with an expiration date
        that has already passed. Note that some clients require a path
        to be specified - this path must exactly match the path given
        when creating the cookie. The path can be specified as a keyword
        argument.
        If the value of a keyword argument is None, it will be ignored.
        """

    def setCookie(name, value, **kw):
        """Sets an HTTP cookie on the browser

        The response will include an HTTP header that sets a cookie on
        cookie-enabled browsers with a key "name" and value
        "value". This overwrites any previously set value for the
        cookie in the Response object.
        If the value of a keyword argument is None, it will be ignored.
        """

    def getCookie(name, default=None):
        """Gets HTTP cookie data as a dict

        Returns the dict of values associated with an HTTP cookie set in the
        response, or 'default' if no such cookie has been set in the response
        yet.
        """

    def redirect(location, status=302):
        """Causes a redirection without raising an error.
        """


class IHTTPPublisher(IPublishTraverse):
    """HTTP-Specific Traversal."""
