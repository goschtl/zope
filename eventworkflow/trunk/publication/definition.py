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

# This process definition (re)uses a review subprocess defined
# in eventworkflow.review

import zope.interface
import zope.event
import zope.app.zapi
import eventworkflow.event
import interfaces

from eventworkflow.review.definition import ReviewProcess
from eventworkflow.interfaces import IActivity

from zope.app.annotation.interfaces import IAnnotations, IAttributeAnnotatable

class PublicationWorkflow:
    zope.interface.implements(interfaces.IPublicationProcess)
	
    def __init__(self):
		self.activities = []
		self.workflowData = {}
		zope.event.notify(eventworkflow.event.ProcessStartedEvent(self))

# the activities
class BaseActivity:
	def __init__(self, pi):
		self.processInstance = pi
		
class CreateArticleActivity(BaseActivity):
	zope.interface.implements(interfaces.ICreateArticleActivity)
	
class PublishOnlineActivity(BaseActivity):
	zope.interface.implements(interfaces.IPublishOnlineActivity)

class PublishDeadTreeActivity(BaseActivity):
	zope.interface.implements(interfaces.IPublishDeadTreeActivity)

class DoPressReleaseActivity:
	zope.interface.implements(interfaces.IDoPressReleaseActivity)

	def __init__(self, pi):
		self.processInstance = pi
		self.state = 'waiting'

	def activate(self):
		self.state = 'active'
		#XXXcreate work items


# the review sub process

#XXX I wonder if this could also be implemented using an adapter
# from IReviewProcess to IActivity

class ReviewSubProcess(ReviewProcess):
	zope.interface.implements(IActivity,
							  ReviewProcess.__provides__)

	def __init__(self, pi):
		self.processInstance = pi
		ReviewProcess.__init__(self)


# 2 more generic handlers

def cleanupFinishedActivities(event):
	"""Remove finished activities from process"""	
	process = event.object.processInstance
	process.activities.remove(event.object)

def handleFinishedSubprocess(event):
	"""What happens with subprocess data

	This handler writes the subflow data to the parents
	workflow data (dict update for now)
	"""
	pi = event.object
	parent = pi.processInstance

	if parent is None: # not a sub process
		return
	
	data = pi.workflowData
	parent.workflowData.update(data)

	zope.event.notify(eventworkflow.event.ActivityFinishedEvent(pi))
	
def startCreateArticle(pi, event):
	"""start the initial activities of the process"""
	pi.activities.append(CreateArticleActivity(pi))

def handleFinishedCreateArticle(activity, event):
	"""Transitions from CreateArticleActivity"""

	pi = activity.processInstance
	
	# start the review sub process
	pi.activities.append(ReviewSubProcess(pi))

def handleFinishedReviewArticle(activity, event):
	"""Transitions from Review Article
	"""
	
	pi = activity.processInstance
	
	data = pi.workflowData

	# OR-split
	if data.get('reviewDecision', None) == 'accept':
		# AND-split
		pi.activities.append(PublishOnlineActivity(pi))
		pi.activities.append(PublishDeadTreeActivity(pi))

	else:
		pi.activities.append(CreateArticleActivity(pi))


AnnotationKey="pubwf.activitycount"

def handlePublications(activity, event):
	"""Transitions from article publications to press release

	This functions handles the transition to the
	DoPressReleaseActivity.	It ensures that both
	publication activities are finished before
	activating the press release activity. (AND-Join)
	"""
	process = activity.processInstance

	# get an IDoPressRelease from process activities, should be just 1
	activities = [x for x in process.activities
					 if interfaces.IDoPressReleaseActivity.providedBy(x)]

	try:
		next_activity = activities.pop()
	except IndexError:
		next_activity = None
	
	if not next_activity:
		next_activity = DoPressReleaseActivity(activity.processInstance)
		process.activities.append(next_activity)

		# put an annotation onto activity
		annotation = IAnnotations(next_activity)
		annotation[AnnotationKey] = 1
	else:
		annotation = IAnnotations(next_activity)
		count = annotation.get(AnnotationKey, 0)
		count += 1

		annotation[AnnotationKey] = count
		
		if count == 2:
			next_activity.activate()
			#XXX maybe remove annotation
