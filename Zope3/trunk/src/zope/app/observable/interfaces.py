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

    def handle(interfaces, handler):
        """Register a handler for some interfaces

        The handler will be called with object's implementing the
        interface.  Typically, one of the objects will be an
        event. Other objects may be associated objects.
        
        """

    def unhandle(interfaces, handler):
        """Unregister a handler for some interfaces
        """
