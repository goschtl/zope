##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Base class for zc.selenium's active resources.

"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.publisher.browser
import zope.publisher.interfaces.browser

import zope.app.publisher.browser.resource


class ResourceBase(zope.publisher.browser.BrowserView,
                   zope.app.publisher.browser.resource.Resource):

    zope.interface.implements(
        zope.publisher.interfaces.browser.IBrowserPublisher)

    def __init__(self, request):
        self.request = request
        self.context = self

    def publishTraverse(self, request, name):
        raise NotFound(None, name)

    def browserDefault(self, request):
        return getattr(self, request.method), ()
