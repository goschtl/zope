##############################################################################
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
##############################################################################
"""HTTPP-specific traversers

For straight HTTP, we need to be able to create null resources.
We also never traverse to views.

$Id: traversal.py,v 1.1 2003/02/07 15:59:37 jim Exp $
"""
__metaclass__ = type

from zope.publisher.interfaces import IPublishTraverse
from zope.app.interfaces.container import ISimpleReadContainer, IItemContainer
from zope.app.http.put import NullResource
from zope.exceptions import NotFoundError

class ContainerTraverser:
    
    __implements__ = IPublishTraverse
    __used_for__ = ISimpleReadContainer

    def __init__(self, container, request):
        self.context = container
        self.request = request

    def publishTraverse(self, request, name):
        subob = self.context.get(name, None)
        if subob is None:
            subob = self.nullResource(request, name)

        return subob

    def nullResource(self, request, name):
        # we traversed to something that doesn't exist.

        # The name must be the last name in the path, so the traversal
        # name stack better be empty:
        if request.getTraversalStack():
            raise NotFoundError(self.context, name, request)

        # This should only happen for a PUT:
        if request.method != 'PUT':
            raise NotFoundError(self.context, name, request)

        return NullResource(self.context, name)

class ItemTraverser(ContainerTraverser):

    __used_for__ = IItemContainer

    def publishTraverse(self, request, name):
        context = self.context

        try:
            return context[name]
        except KeyError:
            return self.nullResource(request, name)
