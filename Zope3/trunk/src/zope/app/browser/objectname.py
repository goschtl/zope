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
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""

Revision information:
$Id: objectname.py,v 1.4 2003/04/30 23:37:48 faassen Exp $
"""
from zope.publisher.interfaces.browser import IBrowserView
from zope.app.interfaces.traversing import IObjectName
from zope.app.traversing.adapters import ObjectName, SiteObjectName

class ObjectNameView(ObjectName):

    __implements__ = IBrowserView, IObjectName

    def __init__(self, context, request):
        self.context = context


class SiteObjectNameView(SiteObjectName):

    __implements__ = IBrowserView, IObjectName

    def __init__(self, context, request):
        pass
