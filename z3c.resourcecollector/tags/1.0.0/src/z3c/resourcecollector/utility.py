##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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

import sha
import zope.component

from zope import interface

from interfaces import ICollectorUtility

class Content(object):
    interface.implements(interface.Interface)
    pass

class CollectorUtility(object):
    """utility"""
    interface.implements(ICollectorUtility)

    def __init__(self,content_type):
        self.resources = {}
        self.content_type = content_type

    def getUrl(self,context,request):
        filetoreturn = self.getResources(request)
        x = sha.new()
        x.update(filetoreturn)
        return x.hexdigest()        
        
    def getResources(self, request):
        filetoreturn = ""
        reducedrs = self.resources.values()
        orderedrs = sorted(reducedrs, cmp=lambda a,b: cmp (a['weight'],b['weight']))
        for resource in orderedrs:
            res = zope.component.getAdapter(request,name=resource['resource'])
            res.__name__ = resource['resource']
            filetoreturn += res.browserDefault(request)[0]() + "\n"
        return filetoreturn
        

