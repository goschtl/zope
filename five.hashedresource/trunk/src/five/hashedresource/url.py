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

from zope.component.interfaces import IResource
from zope.interface import implementsOnly
from zope.traversing.browser.interfaces import IAbsoluteURL
import Products.Five.browser.resource
import urllib
import z3c.hashedresource
import zope.component


class HashingURL(zope.traversing.browser.absoluteurl.AbsoluteURL):
    """Inserts a hash of the contents into the resource's URL,
    so the URL changes whenever the contents change, thereby forcing
    a browser to update its cache.
    """

    implementsOnly(IAbsoluteURL)
    zope.component.adapts(IResource,
                          z3c.hashedresource.interfaces.IHashedResourceSkin)

    def __init__(self, context, request):
        self.context = context
        self.request = request

        container = self.context.__parent__
        container_url = str(zope.component.getMultiAdapter(
                (container, self.request), IAbsoluteURL))
        container_url = urllib.unquote(container_url)

        name = self.context.__name__
        if name.startswith('++resource++'):
            name = name[12:]
        if not isinstance(container,
                          Products.Five.browser.resource.DirectoryResource):
            name = '++resource++' + name

        self.url = "%s/%s" % (container_url, name)

    def __str__(self):
        hash = str(z3c.hashedresource.interfaces.IResourceContentsHash(
                self.context))

        first, last = self.url.split('/++resource++')
        return "%s/++noop++%s/++resource++%s" % (first, hash, last)
