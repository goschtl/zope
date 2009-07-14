#############################################################################
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

from zope.component import adapts
from zope.component.interfaces import IResource
from zope.interface import implementsOnly
from zope.traversing.browser.interfaces import IAbsoluteURL
import z3c.hashedresource
import zope.traversing.browser.absoluteurl


class HashingURL(zope.traversing.browser.absoluteurl.AbsoluteURL):
    """Inserts a hash of the contents into the resource's URL,
    so the URL changes whenever the contents change, thereby forcing
    a browser to update its cache.
    """

    implementsOnly(IAbsoluteURL)
    adapts(IResource, z3c.hashedresource.interfaces.IHashedResourceSkin)

    def __init__(self, context, request):
        self.context = context
        self.request = request

        self.name = self.context.__parent__.__name__
        if self.name.startswith('++resource++'):
            self.name = self.name[12:]

    def _site_url(self):
        return self.context.absolute_url().split('/++resource++')[0]

    def __str__(self):
        hash = str(z3c.hashedresource.interfaces.IResourceContentsHash(
                self.context))
        return "%s/++noop++%s/++resource++%s" % (
            self._site_url(), hash, self.name)
