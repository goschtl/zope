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
$Id: IHubEventChannel.py,v 1.1 2002/11/29 15:51:03 stevea Exp $
"""

from Zope.Event.IEventChannel import IEventChannel

class IHubEventChannel(IEventChannel):
    """Event channel that filters hub events.

    It typically lies between the ObjectHub service and an index, so that
    only certain content gets indexed. The extra iterObjectRegistrations
    method is needed for bootstrapping the index with the appropriate objects.
    """

    def iterObjectRegistrations():
        """Returns an iterator of the object registrations.

        An object registration a tuple (location, hib_id, wrapped_object).
        """

