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
$Id: LocalEventChannel.py,v 1.4 2002/10/21 06:22:40 poster Exp $
"""

from LocalSubscribable import LocalSubscribable
from Zope.Event.IEventChannel import IEventChannel
from Zope.ContextWrapper import ContextMethod
from Zope.Proxy.ProxyIntrospection import removeAllProxies
from Zope.Proxy.ContextWrapper import ContextWrapper

class LocalEventChannel:
    # a mix-in: also needs LocalSubscribable to work.
    # LocalSubscribable was in base class but produced
    # TypeError: multiple bases have instance lay-out conflict
    # when used in ProtoServiceEventChannel
    
    __implements__ = IEventChannel
    
    # needs __init__ from Zope.Event.Subscribable (via
    # LocalSubscribable)!!
        
    def notify(wrapped_self, event):
        clean_self=removeAllProxies(wrapped_self)
        
        subscriptionses = clean_self.subscriptionsForEvent(event)
        # that's a non-interface shortcut for
        # subscriptionses = clean_self._registry.getAllForObject(event)

        for subscriptions in subscriptionses:
            
            for subscriber,filter in subscriptions:
                if filter is not None and not filter(event):
                    continue
                ContextWrapper(subscriber, wrapped_self).notify(event)
    
    notify=ContextMethod(notify)

    

    
