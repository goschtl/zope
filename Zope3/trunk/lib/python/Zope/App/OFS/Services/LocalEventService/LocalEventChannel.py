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
$Id: LocalEventChannel.py,v 1.2 2002/06/10 23:28:10 jim Exp $
"""

from LocalSubscribable import LocalSubscribable
from Zope.Event.IEventChannel import IEventChannel
from Zope.ContextWrapper import ContextMethod
from Zope.Proxy.ProxyIntrospection import removeAllProxies
from Zope.Proxy.ContextWrapper import ContextWrapper

class LocalEventChannel(LocalSubscribable):
    
    __implements__ = IEventChannel
        
    def notify(wrapped_self, event):
        clean_self=removeAllProxies(wrapped_self)
        
        subscriptionses = clean_self._registry.getAllForObject(event)

        for subscriptions in subscriptionses:
            
            for subscriber,filter in subscriptions:
                if filter is not None and not filter(event):
                    continue
                ContextWrapper(subscriber, wrapped_self).notify(event)
    
    notify=ContextMethod(notify)

    

    
