##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
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

from zope import interface
from zope import component

from interfaces import ICollectorUtility


class CollectorUtility(object):
    """utility"""
    interface.implements(ICollectorUtility)

    def __init__(self,content_type):
        self.resources = {}
        self.content_type = content_type

    def getUrl(self,context,request):
        #XXX: fix this workaround :
        #  getting the resources to calculate the hash changes the request,
        #  because the resource getter also sets response headers.
        h = {}
        h.update(request.response._headers)
        filetoreturn = self.getResources(request)
        request.response._headers = h
        x = sha.new()
        x.update(filetoreturn)
        return x.hexdigest()

    def getResources(self, request):
        filetoreturn = ""
        reducedrs = self.resources.values()
        orderedrs = sorted(reducedrs, cmp=lambda a,b: cmp (a['weight'],b['weight']))
        for resource in orderedrs:
            res = component.getAdapter(request,name=resource['resource'])
            res.__name__ = resource['resource']
            filetoreturn += res.GET() + "\n"
        return filetoreturn

