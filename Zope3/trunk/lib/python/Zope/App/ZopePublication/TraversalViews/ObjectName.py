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
$Id: ObjectName.py,v 1.3 2002/07/11 18:21:36 jim Exp $
"""
from Zope.Publisher.Browser.IBrowserView import IBrowserView
from Zope.Proxy.ContextWrapper import getInnerWrapperData
from Zope.App.Traversing.ObjectName \
    import IObjectName, ObjectName, SiteObjectName

from Interface import Interface

class ObjectNameView(ObjectName):

    __implements__ = IBrowserView, IObjectName
    
    def __init__(self, context, request):
        self.context = context


class SiteObjectNameView(SiteObjectName):

    __implements__ = IBrowserView, IObjectName
    
    def __init__(self, context, request):
        pass
