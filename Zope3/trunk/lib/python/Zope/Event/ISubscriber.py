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
$Id: ISubscriber.py,v 1.2 2002/06/10 23:29:25 jim Exp $
"""

from Interface import Interface

class ISubscriber(Interface):
    """Interface for objects which receiving event notifications."""

    def notify(event):
        """ISubscribables call this method to indicate an event.

        This method must not block!

        This method may raise an exception to veto the event.
        """

class IIndirectSubscriber(ISubscriber):
    """Interface for objects that handle subscriptions for another object"""
    
    def __eq__(other):
        """this standard python hook allows indirect subscribers to
        participate in subscribable introspection and unsubscription
        without being the actual original subscriber object"""

    
    
