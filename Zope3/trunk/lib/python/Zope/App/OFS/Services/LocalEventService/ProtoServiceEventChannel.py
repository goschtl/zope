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
"""An event channel that wants to subscribe to the nearest parent
event service when bound, and unsubscribe
when unbound, as one needs for an event channel that will be a service

$Id: ProtoServiceEventChannel.py,v 1.4 2002/12/12 20:05:51 jack-e Exp $
"""

from Zope.App.Traversing.ITraverser import ITraverser
from Zope.Proxy.ProxyIntrospection import removeAllProxies
from Zope.ComponentArchitecture import getAdapter, getService
from LocalSubscriptionAware import LocalSubscriptionAware
from Zope.ContextWrapper import ContextMethod
from LocalEventChannel import LocalEventChannel
from LocalServiceSubscribable import LocalServiceSubscribable
from Zope.App.OFS.Services.ServiceManager.IBindingAware import IBindingAware
from Zope.Proxy.ContextWrapper import isWrapper
from Zope.Event.IEvent import IEvent

class ProtoServiceEventChannel(
    LocalSubscriptionAware,
    LocalServiceSubscribable,
    LocalEventChannel):
    """An event channel that wants to subscribe to the nearest
    event service when bound, and unsubscribe when unbound, as one
    needs for an event channel that will be a service"""
    
    __implements__ = (
        LocalEventChannel.__implements__,
        LocalServiceSubscribable.__implements__,
        LocalSubscriptionAware.__implements__,
        IBindingAware
        )
    
    def __init__(self):
        LocalServiceSubscribable.__init__(self)
        LocalSubscriptionAware.__init__(self)
    
    subscribeOnBind = True
        # if true, event service will subscribe
        # to the parent event service on binding, unless the parent
        # service is the global event service; see 'bound' method
        # below
    
    _serviceName = None
        # the name of the service that this object is providing, or
        # None if unbound
    
    _subscribeToServiceName = "Events"
    _subscribeToServiceInterface = IEvent
    _subscribeToServiceFilter = None
    
    def bound(wrapped_self, name):
        "see IBindingAware"
        clean_self = removeAllProxies(wrapped_self)
        clean_self._serviceName = name # for LocalServiceSubscribable
        if clean_self.subscribeOnBind:
            es = getService(wrapped_self, clean_self._subscribeToServiceName)
            if isWrapper(es):
                # if we really want to receive events from a
                # global event-type service we're going to have to
                # set something special up -- something that subscribes
                # every startup...
                es.subscribe(
                    wrapped_self,
                    clean_self._subscribeToServiceInterface,
                    clean_self._subscribeToServiceFilter
                    )
    
    bound = ContextMethod(bound)
    
    def unbound(wrapped_self, name):
        "see IBindingAware"
        clean_self = removeAllProxies(wrapped_self)
        for subscription in clean_self._subscriptions:
            subscribable = getAdapter(
                wrapped_self, ITraverser).traverse(subscription[0])
            subscribable.unsubscribe(wrapped_self)
        clean_self._subscriptions = ()
        clean_self._serviceName = None

    unbound = ContextMethod(unbound)
    
