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
"""
    Define view component for folder contents.
"""

import os

from Zope.Publisher.Browser.IBrowserPublisher import IBrowserPublisher
from Zope.Publisher.XMLRPC.IXMLRPCPublisher import IXMLRPCPublisher
from Zope.Publisher.Exceptions import NotFound
from IContainer import IReadContainer, IItemContainer
from Zope.ComponentArchitecture import queryView
from Zope.ComponentArchitecture import getDefaultViewName


class ContainerTraverser:

    __implements__ = IBrowserPublisher, IXMLRPCPublisher
    __used_for__ = IReadContainer

    def __init__(self, container, request):
        self.context = container

    def publishTraverse(self, request, name):
        c = self.context

        subob = c.get(name, None)
        if subob is None:

            view = queryView(c, name, request)
            if view is not None:
                return view

            raise NotFound(c, name, request)

        return subob

    def browserDefault(self, request):
        c = self.context
        view_name = getDefaultViewName(c, request)
        view_uri = "@@%s" % view_name
        return c, (view_uri,)


class ItemTraverser(ContainerTraverser):

    __used_for__ = IItemContainer

    def publishTraverse(self, request, name):
        context = self.context

        try:            
            return context[name]

        except KeyError:
            view = queryView(context, name, request)
            if view is not None:
                return view

        raise NotFound(context, name, request)
