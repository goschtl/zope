##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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

$Id: Resource.py,v 1.3 2002/07/12 22:11:03 jim Exp $
"""
__metaclass__ = type # All classes are new style when run with Python 2.2+

from Zope.ComponentArchitecture import queryView
from Zope.Proxy.ContextWrapper import getWrapperContainer, getInnerWrapperData
from Zope.ContextWrapper import ContextMethod

class Resource:

    def __init__(self, request):
        self.request = request

    def __call__(self):
        name = getInnerWrapperData(self)['name']
        if name.startswith('++resource++'):
            name = name[12:]

        service = getWrapperContainer(self)
        site = getWrapperContainer(service)

        skin = self.request.getPresentationSkin()
        if skin:
            skin = "++skin++%s/" % skin

        if site is None:
            return "/%s@@/%s" % (skin, name)

        absolute_url = queryView(service, 'absolute_url', self.request)

        if absolute_url is None:
            return "/%s@@/%s" % (skin, name)

        site_url = absolute_url()
        
        return "%s/%s@@/%s" % (site_url, skin, name)

    __call__ = ContextMethod(__call__)
