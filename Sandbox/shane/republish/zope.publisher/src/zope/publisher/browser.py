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
"""Browser-specific base classes

$Id: browser.py 96546 2009-02-14 20:48:37Z shane $
"""

from zope.interface import implements
from zope.location import Location

from zope.publisher.interfaces.browser import IBrowserPage
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.exceptions import NotFound


class BrowserView(Location):
    """Browser View base class.

    See the tests in README.txt.
    """
    implements(IBrowserView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _getParent(self):
        return getattr(self, '_parent', self.context)

    def _setParent(self, parent):
        self._parent = parent

    __parent__ = property(_getParent, _setParent)


class BrowserPage(BrowserView):
    """Browser page base class.

    See the tests in README.txt.
    """
    implements(IBrowserPage)

    def browserDefault(self, request):
        return self, ()

    def publishTraverse(self, request, name):
        raise NotFound(self, name, request)

    def __call__(self, *args, **kw):
        raise NotImplementedError("Subclasses should override __call__ to "
                                  "provide a response body")
