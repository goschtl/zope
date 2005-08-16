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

"""State related events

$Id:$
"""

from zope.interface import implements
from zope.app.event.objectevent import ObjectEvent

from interfaces import IStatePermissionsRolesMappingUpdateEvent

class StatePermissionsRolesMappingUpdateEvent(ObjectEvent):
    """State Update Permissions Roles Mapping Event
    """

    implements(IStatePermissionsRolesMappingUpdateEvent)

    def __init__(self, object, mapping):
        """Constructor
        """
        super(StatePermissionsRolesMappingUpdateEvent,
              self).__init__(object)
        self.mapping = mapping
