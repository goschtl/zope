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

"""Process Definition Transition Changed Events

$Id:$
"""

from zope.interface import implements
from zope.app.event.objectevent import ObjectEvent

from interfaces import IProcessDefinitionAddPermissionsEvent
from interfaces import IProcessDefinitionDelPermissionsEvent

class ProcessDefinitionAddPermissionsEvent(ObjectEvent):
    """Process Definition Add Permissions event
    """

    implements(IProcessDefinitionAddPermissionsEvent)

    def __init__(self, object, permissions_to_add=[]):
        """Constructor
        """
        super(ProcessDefinitionAddPermissionsEvent, self).__init__(object)
        self.permissions_to_add = permissions_to_add

class ProcessDefinitionDelPermissionsEvent(ObjectEvent):
    """Process Definition Del Permissions event
    """

    implements(IProcessDefinitionDelPermissionsEvent)

    def __init__(self, object, permissions_to_remove=[]):
        """Constructor
        """
        super(ProcessDefinitionDelPermissionsEvent, self).__init__(object)
        self.permissions_to_remove = permissions_to_remove
