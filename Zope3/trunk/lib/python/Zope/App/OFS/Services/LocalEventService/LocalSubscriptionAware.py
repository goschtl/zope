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
$Id: LocalSubscriptionAware.py,v 1.2 2002/06/10 23:28:10 jim Exp $
"""
from Zope.Event.ISubscriptionAware import ISubscriptionAware
from Zope.Proxy.ProxyIntrospection import removeAllProxies
from Zope.ComponentArchitecture import getAdapter
from Zope.App.Traversing.ITraverser import ITraverser


class LocalSubscriptionAware:
    # a mix-in
    
    __implements__=ISubscriptionAware
    
    def __init__(self):
        self._subscriptions=()
    
    def subscribedTo(self, subscribable, event_type, filter):
        #subscribable_path=getAdapter(
         #   subscribable, ITraverser).getPhysicalPath()
        subscribable_path="/%s" % "/".join(getAdapter(
            subscribable, ITraverser).getPhysicalPath())
        # XXX right now the conversion to a string is necessary because
        # the tuple path returned by the Traverser does not include an
        # empty initial space to represent the root
        if (subscribable_path, event_type, filter) not in self._subscriptions:
            self._subscriptions+=((subscribable_path,event_type, filter),)
    
    def unsubscribedFrom(self, subscribable, event_type, filter):
        subscribable_path="/%s" % "/".join(getAdapter(
            subscribable, ITraverser).getPhysicalPath())
        sub=list(self._subscriptions)
        sub.remove((subscribable_path, event_type, filter))
        self._subscriptions=tuple(sub)
        
        
        