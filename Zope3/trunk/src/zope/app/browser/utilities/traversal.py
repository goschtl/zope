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
"""Specific HTTP

$Id: traversal.py,v 1.5 2003/10/18 18:56:23 sidnei Exp $
"""
from zope.interface import implements
from zope.component import getDefaultViewName, queryView
from zope.publisher.interfaces import IPublishTraverse
from zope.app.interfaces.utilities.schema import IMutableSchema

from zope.exceptions import NotFoundError

from zope.proxy import removeAllProxies

from zope.app.interfaces.traversing import ITraversable
from zope.app.traversing.namespace import UnexpectedParameters
from zope.app.interfaces.location import ILocation

_marker = object()

class SchemaFieldTraverser:

    implements(IPublishTraverse)
    __used_for__ = IMutableSchema

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        subob = self.context.get(name, None)

        # XXX: Check that subobj has self.context as parent!
        # YYY: Why?

        if subob is None:

            view = queryView(self.context, name, request)
            if view is not None:
                if ILocation.isImplementedBy(view):
                    view.__parent__ = self.context
                    view.__name__ = name

                return view

            raise NotFoundError(self.context, name, request)

        return subob

    def browserDefault(self, request):
        c = self.context
        view_name = getDefaultViewName(c, request)
        view_uri = "@@%s" % view_name
        return c, (view_uri,)

class SchemaFieldTraversable:
    """Traverses Schema Fields.
    """

    implements(ITraversable)
    __used_for__ = IMutableSchema

    def __init__(self, context):
        self._context = context

    def traverse(self, name, parameters, original_name, furtherPath):
        if parameters:
            raise UnexpectedParameters(parameters)

        subobj = self._context.get(name, _marker)
        if subobj is _marker:
            raise NotFoundError, original_name

        return subobj
