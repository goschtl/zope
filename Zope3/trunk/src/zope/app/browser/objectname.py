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
$Id: objectname.py,v 1.5 2003/06/04 11:13:47 stevea Exp $
"""
from zope.publisher.interfaces.browser import IBrowserView
from zope.app.traversing.adapters import ObjectName, SiteObjectName
from zope.interface import implements

class ObjectNameView(ObjectName):

    implements(IBrowserView)

    def __init__(self, context, request):
        self.context = context


class SiteObjectNameView(SiteObjectName):

    implements(IBrowserView)

    def __init__(self, context, request):
        pass
