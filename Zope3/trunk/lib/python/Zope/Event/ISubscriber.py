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
$Id: ISubscriber.py,v 1.4 2002/11/11 08:33:45 stevea Exp $
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
    """Interface for objects that handle subscriptions for another object."""
    
    def __eq__(other):
        """Compare two indirect subscribers

        Two indirect subscribers are the same if they reference the
        same object.
        """

    
    
