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
from zope.app.annotation.interfaces import IAttributeAnnotatable

import zope.app.event.interfaces

### Event Interfaces
class IActivityFinishedEvent(zope.app.event.interfaces.IObjectEvent):
	"""Signal a finished activity"""

class IProcessStartedEvent(zope.app.event.interfaces.IObjectEvent):
	"""Signal starting a process"""

class IProcessFinishedEvent(zope.app.event.interfaces.IObjectEvent):
	"""Signal finished process"""

class IWorkitemFinishedEvent(zope.app.event.interfaces.IObjectEvent):
	"""Signal a finished workitem"""
	
### WfMC type entities in a workflow
# we're not heading for compliance yet
class IProcess(zope.interface.Interface):
	"""An instance of a process (definition)

	An IProcessStartedEvent is generated in the constructor.
	"""

	activities = zope.interface.Attribute(
		"list of current activities")

	workflowData = zope.interface.Attribute(
		"data associated with the process")
	
class IActivity(zope.interface.Interface):
	"""An instance of a specific activity"""

	processDefinition = zope.interface.Attribute(
		"a reference to the process the activity belongs to")

	def __init__(pi):
		"""constructs new instance

		pi - process instance the activity belongs to
		"""
		
class IJoiningActivity(IActivity, IAttributeAnnotatable):
	"""Activity that is activated after a join in the workflow

	This is used for stateful activities, that are needed after
	AND-joins without workflow data related preconditions, i.e.
	all predecessors must be finished
	"""
	
	state = zope.interface.Attribute(
		"the state of the activity instance, one of waiting/active")
	
	def activate():
		"""activate activity

		activity instances start in a waiting state. This methods
		propagates them to the active state and creates the
		work items.
		"""


class IWorklistUtility(zope.interface.Interface):
	"""Manage workitems in workflows"""
	
	def addWorkitem(item):
		"""Add new IWorkitem"""
	
	def itemsFor(principalId):
		"""Return list of all workitems for a principal

		Returns empty list if no principal can be
		retrieved for the given id. If the principal
		belongs to groups, also the workitems assigned
		to these groups are returned.
		"""

class IWorkitem(zope.interface.Interface):
	"""A single workitem"""

	activity = zope.interface.Attribute(
		"activity this work item belongs to")

	description = zope.schema.TextLine(
		title = u'Description',
		)
	
	principals = zope.schema.List(
		title = u"Principals",
		value_type = zope.schema.TextLine(),
		)

