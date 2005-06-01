##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Observable interfaces

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface.interfaces import Interface

class IObservable(Interface):

    def notify(event):
        """Call registered event handlers"""

    def handle(interfaces, handler):
        """Register a `handler` for some `interfaces`

        The handler will be called with object's implementing the
        interface.  Typically, one of the objects will be an
        event. Other objects may be associated objects.

        Note that, at this time, only handlers taking a single
        argument, an event, will be called, because there isn't
        currently an api for accessing more complex subscribers. There
        will be in the future though.
        
        """

    def unhandle(interfaces, handler):
        """Unregister a `handler` for some `interfaces`
        """
