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
$Id: IEventService.py,v 1.3 2002/09/05 21:41:09 jeremy Exp $
"""

from ISubscribable import ISubscribable

class IEventService(ISubscribable):
    """The EventService service is the 'root channel'.
    
    Its subscribers include other channels.

    It is also the 'default destination' for events
    when they are generated.
    """
    
    def publishEvent(event):
        """Notify all subscribers of the channel of event.

        Events will often be propagated to higher level IEventServices;
        This is a policy decision for the IEventService.
        """

    

    
