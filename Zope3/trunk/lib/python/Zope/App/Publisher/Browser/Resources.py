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
"""Resource URL acess

$Id: Resources.py,v 1.3 2002/10/28 11:41:34 stevea Exp $
"""
__metaclass__ = type # All classes are new style when run with Python 2.2+

from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.Publisher.Browser.IBrowserPublisher import IBrowserPublisher
from Zope.ComponentArchitecture import getService
from Zope.Proxy.ContextWrapper import ContextWrapper
from Zope.ContextWrapper import ContextMethod
from Zope.Exceptions import NotFoundError

class Resources(BrowserView):
    """Provide a URL-accessible resource namespace
    """

    __implements__ = BrowserView.__implements__, IBrowserPublisher

    ############################################################
    # Implementation methods for interface
    # Zope.Publisher.Browser.IBrowserPublisher.

    def publishTraverse(wrapped_self, request, name):
        '''See interface IBrowserPublisher'''
        
        resource_service = getService(wrapped_self, 'Resources')
        resource = resource_service.queryResource(wrapped_self, name, request)
        if resource is None:
            raise NotFoundError(wrapped_self, name)
        return ContextWrapper(resource, resource_service)

    publishTraverse = ContextMethod(publishTraverse)

    def browserDefault(self, request):
        '''See interface IBrowserPublisher'''
        return empty, ()
        
    #
    ############################################################

def empty():
    return ''
