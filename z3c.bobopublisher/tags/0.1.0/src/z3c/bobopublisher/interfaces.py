##############################################################################
#
# Copyright (c) 2009 Fabio Tranchitella <fabio@tranchitella.it>
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

"""
$Id$
"""

from zope.interface import Interface


class IPublishTraverse(Interface):
    """Interface for publish traverse adapters"""

    def publishTraverse(request, name):
        """Lookup a name

        The 'request' argument is the publisher request object.  The
        'name' argument is the name that is to be looked up; it must
        be an ASCII string or Unicode object.

        If a lookup is not possible, raise a KeyError error.
        """


class IDefaultViewName(Interface):
    """Marker interface for the bobo:defaultView directive"""


class IRequest(Interface):
    """Interface for webob.Request objects"""


class IGETRequest(IRequest):
    """Interface for webob.Request objects (GET method)"""


class IPOSTRequest(IRequest):
    """Interface for webob.Request objects (POST method)"""


class IPUTRequest(IRequest):
    """Interface for webob.Request objects (PUT method)"""


class IDELETERequest(IRequest):
    """Interface for webob.Request objects (DELETE method)"""


class IAbsoluteURL(Interface):
    """Absolute URL"""

    def __unicode__():
        """Returns the URL as a unicode string."""

    def __str__():
        """Returns an ASCII string with all unicode characters url quoted."""

    def __repr__():
        """Get a string representation"""

    def __call__():
        """Returns an ASCII string with all unicode characters url quoted."""

    def breadcrumbs():
        """Returns a tuple like ({'name':name, 'url':url}, ...)

        Name is the name to display for that segment of the breadcrumbs.
        URL is the link for that segment of the breadcrumbs.
        """
