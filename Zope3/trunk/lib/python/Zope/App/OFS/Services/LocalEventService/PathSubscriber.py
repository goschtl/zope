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
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
"""

Revision information:
$Id: PathSubscriber.py,v 1.5 2002/12/12 21:05:48 poster Exp $
"""

from Zope.ComponentArchitecture import getAdapter
from Zope.App.Traversing.ITraverser import ITraverser
from Zope.Event.ISubscriptionAware import ISubscriptionAware
from Zope.Proxy.ProxyIntrospection import removeAllProxies
from IPathSubscriber import IPathSubscriber
from Interface import Attribute
from Zope.App.Traversing import getPhysicalPathString, traverse

from Zope.ContextWrapper import ContextMethod

class AbstractIndirectSubscriber:
    
    def notify(wrapped_self, event):
        removeAllProxies(wrapped_self)._getSubscriber(
            wrapped_self).notify(event)
    
    notify=ContextMethod(notify)
    
    def subscribedTo(wrapped_self, subscribable, event_type, filter):
        proxiedObj = removeAllProxies(
            wrapped_self)._getSubscriber(wrapped_self)
        if ISubscriptionAware.isImplementedBy(
            removeAllProxies(proxiedObj)):
            proxiedObj.subscribedTo(
                subscribable, event_type, filter )
    
    subscribedTo=ContextMethod(subscribedTo)
    
    def unsubscribedFrom(wrapped_self, subscribable, event_type, filter):
        proxiedObj = removeAllProxies(
            wrapped_self)._getSubscriber(wrapped_self)
        if ISubscriptionAware.isImplementedBy(
            removeAllProxies(proxiedObj)):
            proxiedObj.unsubscribedFrom(
                subscribable, event_type, filter )
    
    unsubscribedFrom=ContextMethod(unsubscribedFrom)

class PathSubscriber(AbstractIndirectSubscriber):
    
    __implements__ = IPathSubscriber, ISubscriptionAware
    
    def __init__(self, wrapped_subscriber):
        self.subscriber_path = getPhysicalPathString(wrapped_subscriber)
    
    def __eq__(self, other):
        return (IPathSubscriber.isImplementedBy(other) and 
               other.subscriber_path == self.subscriber_path)
    
    def _getSubscriber(self, wrapped_self):
        return traverse(wrapped_self, self.subscriber_path)
