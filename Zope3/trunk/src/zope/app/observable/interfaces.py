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

$Id$
"""

from zope.interface.interfaces import Interface

class IObservable(Interface):

    def notify(event):
        """Notify the ISubscriber subscribers"""

    def subscribe(required, provided, subscriber):
        """Subscribe to an event for a particular instance.


        Note that the providd interface should be or extend ISubscriber.

        In the future, we will provide a subscribers function that
        allows other interfaces to be used.
        
        """
