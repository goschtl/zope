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
import unittest
from zope.testing.doctest import DocFileSuite, DocTestSuite
import eventworkflow.review.tests.setup

from zope.app.tests import placelesssetup, ztapi
from zope.app.tests.setup import setUpAnnotations

import eventworkflow.interfaces
import eventworkflow.publication.interfaces
import eventworkflow.publication.definition
import eventworkflow.review.interfaces

def setUp(test):
	eventworkflow.review.tests.setup.setUp(test)

	ztapi.subscribe([eventworkflow.interfaces.IProcessFinishedEvent],
   					None,
   					eventworkflow.publication.definition.handleFinishedSubprocess)
	
	ztapi.subscribe([eventworkflow.publication.interfaces.IPublicationProcess,
                     eventworkflow.interfaces.IProcessStartedEvent],
   					None,
   					eventworkflow.publication.definition.startCreateArticle)
	ztapi.subscribe([eventworkflow.publication.interfaces.ICreateArticleActivity,
                     eventworkflow.interfaces.IActivityFinishedEvent],
   					None,
   					eventworkflow.publication.definition.handleFinishedCreateArticle) 
	ztapi.subscribe([eventworkflow.review.interfaces.IReviewProcess,
                     eventworkflow.interfaces.IActivityFinishedEvent],
   					None,
   					eventworkflow.publication.definition.handleFinishedReviewArticle)
	ztapi.subscribe([eventworkflow.publication.interfaces.IPublishOnlineActivity,
                     eventworkflow.interfaces.IActivityFinishedEvent],
   					None,
   					eventworkflow.publication.definition.handlePublications)
	ztapi.subscribe([eventworkflow.publication.interfaces.IPublishDeadTreeActivity,
                     eventworkflow.interfaces.IActivityFinishedEvent],
   					None,
   					eventworkflow.publication.definition.handlePublications)
	
	setUpAnnotations()

def test_suite():
    suite = unittest.TestSuite((
		DocFileSuite('simplesub.txt',
					 setUp=setUp,
					 tearDown=placelesssetup.tearDown),

							   ))

    return suite
