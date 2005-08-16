##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Bobo Publication

$Id$
"""

from zope.event import notify
import zope.interface

from zope.bobo.interfaces import BeginRequest
from zope.bobo.interfaces import BeforeTraverse
from zope.bobo.interfaces import AfterTraversal
from zope.bobo.interfaces import AfterCall
from zope.bobo.interfaces import PublicationException
from zope.bobo.interfaces import EndRequest

from zope.component import queryMultiAdapter
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.interfaces.browser import IBrowserPublication
from zope.publisher.publish import mapply
from zope.security.checker import ProxyFactory

class Publication(object):

    zope.interface.implements(IBrowserPublication)

    def __init__(self, resource_factory):
        self.resource_factory = resource_factory
    
    def beforeTraversal(self, request):
        notify(BeginRequest(request))

    def getApplication(self, request):
        return ProxyFactory(self.resource_factory(request))

    def callTraversalHooks(self, request, ob):
        notify(BeforeTraverse(request, ob))
        

    def traverseName(self, request, ob, name):
        if not IPublishTraverse.providedBy(ob):
            ob = queryMultiAdapter((ob, request), IPublishTraverse)
            if ob is None:
                raise NotFound(ob, name, request)
        ob = ob.publishTraverse(request, name)

        ob = ProxyFactory(ob)

        return ob

    def getDefaultTraversal(self, request, ob):
        if IBrowserPublisher.providedBy(ob):
            # ob is already proxied, so the result of calling a method will be
            return ob.browserDefault(request)
        else:
            adapter = queryMultiAdapter((ob, request), IBrowserPublisher)
            if adapter is None:
                # We don't allow publication of non browser publishers
                raise NotFound(ob, '', request)
            ob, path = adapter.browserDefault(request)
            ob = ProxyFactory(ob)
            return ob, path
        
    def afterTraversal(self, request, ob):
        notify(AfterTraversal(request, ob))

    def callObject(self, request, ob):
        return mapply(ob, request.getPositionalArguments(), request)

    def afterCall(self, request, ob):
        notify(AfterCall(request, ob))

    def handleException(self, ob, request, exc_info, retry_allowed=1):
        raise exc_info[0], exc_info[1], exc_info[2]
        notify(PublicationException(request, ob, exc_info, retry_allowed))

    def endRequest(self, request, ob):
        """Do any end-of-request cleanup
        """
        notify(EndRequest(request, ob))
            
