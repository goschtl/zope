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
$Id: IEventService.py,v 1.7 2002/12/21 15:32:59 poster Exp $
"""

from ISubscribable import ISubscribable
from IEvent import IEvent

class IEventService(ISubscribable):
    """The EventService service is the 'root channel'.
    
    Its subscribers include other channels.

    It is also the 'default destination' for events
    when they are generated.
    """
    
    def publish(event):
        """Notify all subscribers of the channel of event.

        Events will often be propagated to higher level IEventServices;
        This is a policy decision for the IEventService.
        """

