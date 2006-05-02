##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
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
"""Machinery for making things viewable

$Id$
"""
import warnings
import zope.deprecation
from zope.interface import implements
from zope.component.interfaces import ComponentLookupError
from zope.app.publisher.browser import getDefaultViewName
from Products.Five.interfaces import IBrowserDefault

class BrowserDefault(object):
    implements(IBrowserDefault)

    def __init__(self, context):
        if zope.deprecation.__show__():
            warnings.warn("The BrowserDefault class is no longer needed and "  \
                          "will be removed in Zope 2.12. \n If you rely on "   \
                          "it to get the default view, replace the call with " \
                          "zope.app.publisher.browser.queryDefaultViewName",
                          DeprecationWarning, 2)
        self.context = context

    def defaultView(self, request):
        context = self.context
        try:
            name = getDefaultViewName(context, request)
            return context, [name,]
        except ComponentLookupError:
            return context, None
