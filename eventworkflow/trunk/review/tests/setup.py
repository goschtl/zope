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
from zope.app.tests import placelesssetup, ztapi
from zope.app.tests.setup import setUpAnnotations

import eventworkflow.review.interfaces
import eventworkflow.review.definition

import eventworkflow.interfaces


def setUpUtilities(test):
	from eventworkflow.interfaces import IWorklistUtility
	from eventworkflow.worklist import BasicWorklistUtility
	
	ztapi.provideUtility(IWorklistUtility, BasicWorklistUtility())


def setUpSubscriptions(test):
	ztapi.subscribe([eventworkflow.interfaces.IActivityFinishedEvent],
   					None,
   					eventworkflow.review.definition.cleanupFinishedActivities)

	ztapi.subscribe([eventworkflow.interfaces.IWorkitemFinishedEvent],
   					None,
   					eventworkflow.review.definition.workitemFinished)
	
	ztapi.subscribe([eventworkflow.review.interfaces.IReviewProcess,
		             eventworkflow.interfaces.IProcessStartedEvent],
   					None,
   					eventworkflow.review.definition.processStarted)

	ztapi.subscribe([eventworkflow.review.interfaces.IAcceptResponsibilityActivity,
		             eventworkflow.interfaces.IActivityFinishedEvent],
   					None,
   					eventworkflow.review.definition.reviewerAssigned)

	ztapi.subscribe([eventworkflow.review.interfaces.IDecideDraftActivity,
		             eventworkflow.interfaces.IActivityFinishedEvent],
   					None,
   					eventworkflow.review.definition.decisionMade)

	ztapi.subscribe([eventworkflow.review.interfaces.IWriteCommentActivity,
		             eventworkflow.interfaces.IActivityFinishedEvent],
   					None,
   					eventworkflow.review.definition.commentWritten)
	
def setUp(test):
	placelesssetup.setUp(test)
	setUpUtilities(test)
	setUpSubscriptions(test)
	setUpAnnotations()
