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
$Id: ISubscriptionAware.py,v 1.2 2002/06/10 23:29:25 jim Exp $
"""
from Interface import Interface

# these are calls and not events because they are traditional messages
# between two objects, not events of general interest.

class ISubscriptionAware(Interface):
    
    def subscribedTo(subscribable, event_type, filter):
        """alerts the object that it has subscribed, via a call from
        itself or from another object, to the subscribable.  The
        event_type and filter match the arguments provided to the
        ISubscribable.subscribe.
        
        The subscribable must be appropriately placefully wrapped (note
        that the global event service will have no wrapping)."""
    
    def unsubscribedFrom(subscribable, event_type, filter):
        """alerts the object that it has unsubscribed, via a call from
        itself or from another object, to the subscribable.  The
        event_type and filter match the exact event_type and filter of
        the deleted subscription, rather than, necessarily, the
        arguments provided to the ISubscribable.unsubscribe.
        
        The subscribable must be appropriately placefully wrapped (note
        that the global event service will have no wrapping)."""