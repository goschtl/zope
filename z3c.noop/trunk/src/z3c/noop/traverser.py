#############################################################################
#
# Copyright (c) 2006-2007 Zope Corporation and Contributors.
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

from zope.component import adapts
from zope.interface import implements, Interface
import zope.publisher.interfaces.browser
import zope.traversing.interfaces


class NoOpTraverser(object):
    """This traverser simply skips a path element,
    so /foo/++noop++qux/bar is equivalent to /foo/bar.

    This is useful for example to generate varying URLs to work around browser
    caches.
    """

    adapts(Interface,  zope.publisher.interfaces.browser.IDefaultBrowserLayer)
    implements(zope.traversing.interfaces.ITraversable)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, furtherPath):
        return self.context
