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
$Id: event.py,v 1.3 2002/12/30 14:03:14 stevea Exp $
"""

from zope.interface import Interface
from zope.app.interfaces.event import ISubscribable, ISubscriber, IPublisher

class ISubscriptionService(ISubscribable):
    """A Subscribable that implements the Subscription service."""

class IEventChannel(ISubscribable, ISubscriber):
    """Interface for objects which distribute events to subscribers. """

class IEventService(ISubscriptionService, IPublisher):
    """Local event service implementation.
    
    Offers the Events and Subscription services.
    """
    
