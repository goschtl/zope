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
$Id: PathSubscriber.py,v 1.3 2002/07/02 23:44:12 jim Exp $
"""

from Zope.ComponentArchitecture import getAdapter
from Zope.App.Traversing.ITraverser import ITraverser
from Zope.Event.ISubscriptionAware import ISubscriptionAware
from Zope.Proxy.ProxyIntrospection import removeAllProxies
from IPathSubscriber import IPathSubscriber
from Interface import Attribute

from Zope.ContextWrapper import ContextMethod


class PathSubscriber:
    
    __implements__=IPathSubscriber, ISubscriptionAware
    
    def __init__(self, wrapped_subscriber):
        self.subscriber_path="/%s" % "/".join(getAdapter(
            wrapped_subscriber, ITraverser).getPhysicalPath())
        # XXX right now the conversion to a string is necessary because
        # the tuple path returned by the Traverser does not include an
        # empty initial space to represent the root
        self.__alert_subscription=ISubscriptionAware.isImplementedBy(
            removeAllProxies(wrapped_subscriber) )
    
    def __eq__(self, other):
        return IPathSubscriber.isImplementedBy(other) and \
               other.subscriber_path==self.subscriber_path
    
    def __getSubscriber(self, wrapped_self):
        traverser = getAdapter(wrapped_self, ITraverser)
        return traverser.traverse(self.subscriber_path)
    
    def notify(wrapped_self, event):
        removeAllProxies(wrapped_self).__getSubscriber(
            wrapped_self).notify(event)
    
    notify=ContextMethod(notify)
    
    def subscribedTo(wrapped_self, subscribable, event_type, filter):
        clean_self=removeAllProxies(wrapped_self)
        if clean_self.__alert_subscription:
            clean_self.__getSubscriber(wrapped_self).subscribedTo(
                subscribable, event_type, filter )
    
    subscribedTo=ContextMethod(subscribedTo)
    
    def unsubscribedFrom(wrapped_self, subscribable, event_type, filter):
        clean_self=removeAllProxies(wrapped_self)
        if clean_self.__alert_subscription:
            clean_self.__getSubscriber(wrapped_self).unsubscribedFrom(
                subscribable, event_type, filter )
    
    unsubscribedFrom=ContextMethod(unsubscribedFrom)
    