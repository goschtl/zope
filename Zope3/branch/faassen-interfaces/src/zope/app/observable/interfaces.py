##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Observable interfaces

$Id: interfaces.py,v 1.2 2004/03/30 14:13:57 nathan Exp $
"""

from zope.interface import implements
from zope.interface.interfaces import Interface, IInterface

class IObservable(Interface):
    
    def notify(event, provided):
        """Notify all subscribers that the event provided has occured."""

    def subscribe(required, provided, subscriber):
        """Subscribe to an event for a particular instance."""
        
