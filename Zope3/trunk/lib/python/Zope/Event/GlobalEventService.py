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
$Id: GlobalEventService.py,v 1.3 2002/08/01 15:33:45 jim Exp $
"""

from IEventService import IEventService
from Subscribable import Subscribable

class GlobalEventService(Subscribable):
    
    __implements__ = IEventService
        
    def publishEvent(self, event):
        
        for subscriptions in self.subscriptionsForEvent(event):
            
            for subscriber, filter in subscriptions:
                if filter is not None and not filter(event):
                    continue
                subscriber.notify(event)
    

eventService = GlobalEventService()


_clear = eventService._clear

# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from Zope.Testing.CleanUp import addCleanUp
addCleanUp(_clear)
del addCleanUp
