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
import zope.interface
import eventworkflow.interfaces

from zope.app.event.objectevent import ObjectEvent

class ProcessStartedEvent(ObjectEvent):
	zope.interface.implements(eventworkflow.interfaces.IProcessStartedEvent)

class ProcessFinishedEvent(ObjectEvent):
	zope.interface.implements(eventworkflow.interfaces.IProcessFinishedEvent)

class ActivityFinishedEvent(ObjectEvent):
	zope.interface.implements(eventworkflow.interfaces.IActivityFinishedEvent)

class WorkitemFinishedEvent(ObjectEvent):
	zope.interface.implements(eventworkflow.interfaces.IWorkitemFinishedEvent)
