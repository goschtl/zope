##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""Some basic traversers for REST

$Id$
"""
import zope.interface
from zope.publisher.interfaces.http import IHTTPPublisher
from zope.app.container.interfaces import IItemContainer
from zope.publisher.interfaces import NotFound
from z3c.rest import interfaces, null

class ItemTraverser(object):
    zope.interface.implements(IHTTPPublisher)
    zope.component.adapts(IItemContainer, interfaces.IRESTRequest)

    def __init__(self, container, request):
        self.context = container
        self.request = request

    def publishTraverse(self, request, name):
        try:
            return self.context[name]
        except KeyError:
            return self.nullResource(request, name)

    def nullResource(self, request, name):
        # we traversed to something that doesn't exist.

        # The name must be the last name in the path, so the traversal
        # name stack better be empty:
        if request.getTraversalStack():
            raise NotFound(self.context, name, request)

        # This should only happen for a PUT:
        if request.method != 'PUT':
            raise NotFound(self.context, name, request)

        return null.NullResource(self.context, name)
