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
"""Define VFS View Traverser for folder contents.

$Id: traverser.py,v 1.2 2002/12/25 14:13:28 jim Exp $
"""

from zope.publisher.interfaces.vfs import IVFSPublisher
from zope.publisher.interfaces import NotFound
from zope.app.interfaces.container import \
     ISimpleReadContainer, IItemContainer
from zope.component import queryView


class ContainerTraverser:

    __implements__ = IVFSPublisher
    __used_for__ = ISimpleReadContainer

    def __init__(self, container, request):
        """Initialize Traverser."""
        self.context = container
        self.request = request

    def _splitExtension(self, name):
        """Split the possible extension from the name"""
        ext_start = name.rfind(".")
        if ext_start > 0:
            return name[:ext_start], name[ext_start:]
        return name, ""

    def publishTraverse(self, request, name):
        """See IPublishTraverse."""
        context = self.context

        # First, try to resolve the name as we get it.
        subob = context.get(name, None)

        if subob is None:
            # It did not work the first time, so let's try without the
            # extension.
            name, ext = self._splitExtension(name)
            subob = context.get(name, None)

        if subob is None:
            view = queryView(context, name, request)
            if view is not None:
                return view

            raise NotFound(context, name, request)

        return subob


class ItemTraverser(ContainerTraverser):

    __used_for__ = IItemContainer

    def publishTraverse(self, request, name):
        """See IPublishTraverse."""
        context = self.context

        # First, try to resolve the name as we get it.
        try:
            return context[name]
        except KeyError:
            pass

        # It did not work the first time, so let's try without the extension.
        name, ext = self._splitExtension(name)
        try:
            return context[name]
        except KeyError:
            view = queryView(context, name, request)
            if view is not None:
                return view

        raise NotFound(context, name, request)
