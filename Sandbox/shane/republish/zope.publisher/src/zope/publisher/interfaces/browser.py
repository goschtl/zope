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
"""Browser-specific interfaces

$Id: browser.py 96546 2009-02-14 20:48:37Z shane $
"""

from zope.interface import Attribute
from zope.interface import Interface
from zope.interface.interfaces import IInterface
from zope.publisher.interfaces.base import IPublishTraverse
from zope.publisher.interfaces.http import IHTTPRequest


class IBrowserRequest(IHTTPRequest):
    """Browser-specific Request functionality.

    The improvement of ``IBrowserRequest`` over ``IHTTPRequest`` is
    that it can hold HTML form data and file uploads in a
    Python-friendly format.
    """
    form = Attribute(
        """Form data

        This is a mapping from name to form value for the name.
        """)

    form_action = Attribute(
        """The :action or :method specified by the form.""")


class IBrowserPublisher(IPublishTraverse):
    """Browser-specific traversal"""

    def browserDefault(request):
        """Provide the default object

        The default object is expressed as a (possibly different)
        object and/or additional traversal steps.

        Returns an object and a sequence of names.  If the sequence of
        names is not empty, then a traversal step is made for each name.
        After the publisher gets to the end of the sequence, it will
        call browserDefault on the last traversed object.

        Normal usage is to return self for object and a default view name.

        The publisher calls this method at the end of each traversal path. If
        a non-empty sequence of names is returned, the publisher will traverse
        those names and call browserDefault again at the end.

        Note that if additional traversal steps are indicated (via a
        nonempty sequence of names), then the publisher will try to adjust
        the base href.
        """

class IBrowserPage(IBrowserPublisher):
    """Browser page"""

    def __call__(*args, **kw):
        """Compute a response body"""

class IBrowserView(Interface):
    """Browser View"""

class IDefaultBrowserLayer(IBrowserRequest):
    """The default layer."""

class IBrowserSkinType(IInterface):
    """A skin is a set of layers."""

class IDefaultSkin(Interface):
    """Any component providing this interface must be a skin.

    This is a marker interface, so that we can register the default skin as an
    adapter from the presentation type to `IDefaultSkin`.
    """

class ISkinChangedEvent(Interface):
    """Event that gets triggered when the skin of a request is changed."""

    request = Attribute("The request for which the skin was changed.")
