# Copyright 2001-2002 Zope Corporation and Contributors.  All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.


from Interface import Interface


class IHeaderOutput (Interface):
    """Interface for setting HTTP response headers.

    This allows the HTTP server and the application to both set response
    headers.

    Zope.Publisher.HTTP.HTTPResponse is optionally passed an
    object which implements this interface in order to intermingle
    its headers with the HTTP server's response headers,
    and for the purpose of better logging.
    """

    def setResponseStatus(status, reason):
        """Sets the status code and the accompanying message.
        """

    def setResponseHeaders(mapping):
        """Sets headers.  The headers must be Correctly-Cased.
        """

    def appendResponseHeaders(lst):
        """Sets headers that can potentially repeat.

        Takes a list of strings.
        """

    def wroteResponseHeader():
        """Returns a flag indicating whether the response

        header has already been sent.
        """

    def setAuthUserName(name):
        """Sets the name of the authenticated user so the name can be logged.
        """
