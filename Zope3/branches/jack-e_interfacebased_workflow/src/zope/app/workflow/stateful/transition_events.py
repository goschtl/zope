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

"""Transition Events

$Id: $
"""

from zope.interface import implements
from zope.app.event.objectevent import ObjectEvent

from interfaces import ITransitionEventUserTriggered

class TransitionUserTriggeredEvent(ObjectEvent):
    """Transition User Triggered Event
    """

    implements(ITransitionEventUserTriggered)

    def __init__(self, object, transition, kwargs={}):
        """Constructor
        """
        super(TransitionUserTriggeredEvent, self).__init__(object)
        self.form_action = transition
        self.kwargs = kwargs
