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
import zope.event
import zope.app.zapi
import eventworkflow.event
import eventworkflow.interfaces
import interfaces

class ReviewProcess:
    zope.interface.implements(interfaces.IReviewProcess)
	
    def __init__(self):
		self.activities = []
		self.workflowData = {}
		zope.event.notify(eventworkflow.event.ProcessStartedEvent(self))

class AcceptResponsibilityActivity:
	zope.interface.implements(interfaces.IAcceptResponsibilityActivity)

	def __init__(self, pi):
		self.processInstance = pi

		# initialize/reset workflow data
		try:
			del pi.workflowData['reviewer']
		except KeyError:
			pass
		
		worklist = zope.app.zapi.getUtility(
			eventworkflow.interfaces.IWorklistUtility)
		
		item = AcceptReviewWI(self,
			"Take responsibility",
			['thomas', 'jim', 'stephan'])
		
		worklist.addWorkitem(item)

	def checkPostCondition(self):
		data = self.processInstance.workflowData
		if data.has_key('reviewer'):
			zope.event.notify(eventworkflow.event.ActivityFinishedEvent(self))

class DecideDraftActivity:
	zope.interface.implements(interfaces.IDecideDraftActivity)

	def __init__(self, pi):
		self.processInstance = pi

	# initialize/reset workflow data
		try:
			del pi.workflowData['reviewDecision']
		except KeyError:
			pass

		worklist = zope.app.zapi.getUtility(
			eventworkflow.interfaces.IWorklistUtility)
		
		item = DecideReviewWI(self,
			"Decide about publication of the reviewed object",
			[pi.workflowData['reviewer']])
		
		worklist.addWorkitem(item)

	def checkPostCondition(self):
		data = self.processInstance.workflowData
		if data.has_key('reviewDecision'):
			zope.event.notify(eventworkflow.event.ActivityFinishedEvent(self))
			
class WriteCommentActivity:
	zope.interface.implements(interfaces.IWriteCommentActivity)

	def __init__(self, pi):
		self.processInstance = pi

		# initialize/reset workflow data
		try:
			del pi.workflowData['reviewComment']
		except KeyError:
			pass

		worklist = zope.app.zapi.getUtility(
			eventworkflow.interfaces.IWorklistUtility)
		
		item = WriteCommentWI(self,
			"Write review comment",
			[pi.workflowData['reviewer']])
		
		worklist.addWorkitem(item)

	def checkPostCondition(self):
		data = self.processInstance.workflowData
		if data.has_key('reviewComment'):
			zope.event.notify(eventworkflow.event.ActivityFinishedEvent(self))


class Workitem:
	"""Just a generic work item prototype

	for testing
	"""
	zope.interface.implements(eventworkflow.interfaces.IWorkitem)
	
	def __init__(self, activity, description, principals):
		self.activity = activity
		self.description = description
		self.principals = principals

	def finish(self):
		zope.event.notify(eventworkflow.event.WorkitemFinishedEvent(self))

class AcceptReviewWI(Workitem):
	def finish(self, reviewerid):
		process = self.activity.processInstance
		data = process.workflowData
		data['reviewer'] = reviewerid

		Workitem.finish(self)

class DecideReviewWI(Workitem):
	def finish(self, decision):
		process = self.activity.processInstance
		data = process.workflowData
		data['reviewDecision'] = decision

		Workitem.finish(self)

class WriteCommentWI(Workitem):
	def finish(self, comment):
		process = self.activity.processInstance
		data = process.workflowData
		data['reviewComment'] = comment

		Workitem.finish(self)



#XXX These 2 handlers might be general workflow handlers

def cleanupFinishedActivities(event):
	"""Remove finished activities from process"""	
	process = event.object.processInstance
	process.activities.remove(event.object)

def workitemFinished(event):
	wi = event.object
	activity = wi.activity

	# remove from worklist
	worklist = zope.app.zapi.getUtility(eventworkflow.interfaces.IWorklistUtility)
	worklist.items.remove(wi)

	# then notify the activity 
	activity.checkPostCondition()



### transition handlers (specific to this process)

def processStarted(process, event):
	"""Activate initial activities"""
	a = AcceptResponsibilityActivity(process)
	process.activities.append(a)

def reviewerAssigned(activity, event):
	pi = activity.processInstance
	
	a = DecideDraftActivity(pi)
	pi.activities.append(a)

def decisionMade(activity, event):
	pi = activity.processInstance

	if pi.workflowData.get('reviewDecision', 'reject') == 'accept':
		zope.event.notify(eventworkflow.event.ProcessFinishedEvent(pi))

	else:
		a = WriteCommentActivity(pi)
		pi.activities.append(a)

def commentWritten(activity, event):
	pi = activity.processInstance
	zope.event.notify(eventworkflow.event.ProcessFinishedEvent(pi))
