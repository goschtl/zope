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

$Id: traversal.py,v 1.3 2003/08/17 06:06:01 philikon Exp $
"""
from zope.interface import implements
from zope.component import getDefaultViewName, queryView
from zope.publisher.interfaces import IPublishTraverse
from zope.app.interfaces.utilities.schema import IMutableSchema

from zope.exceptions import NotFoundError

from zope.proxy import removeAllProxies
from zope.app.context import ContextWrapper

from zope.app.interfaces.traversing import ITraversable
from zope.app.traversing.namespace import UnexpectedParameters

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
        if subob is None:

            view = queryView(self.context, name, request)
            if view is not None:
                return view

            raise NotFoundError(self.context, name, request)

        subob = removeAllProxies(subob)
        return ContextWrapper(subob, self.context, name=name)

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
