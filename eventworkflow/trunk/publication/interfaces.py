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
import eventworkflow.interfaces

class IPublicationProcess(eventworkflow.interfaces.IProcess):
	"""An instance of the example publication process.
	"""
	
class ICreateArticleActivity(eventworkflow.interfaces.IActivity):
	"""Marker interface for 'Create Article' activity"""

class IReviewArticleActivity(eventworkflow.interfaces.IActivity):
	"""Marker interface for 'Review Article' activity"""

class IPublishOnlineActivity(eventworkflow.interfaces.IActivity):
	"""Marker interface for 'Publish online' activity"""

class IPublishDeadTreeActivity(eventworkflow.interfaces.IActivity):
	"""Marker interface for 'Publish on paper' activity"""

class IDoPressReleaseActivity(eventworkflow.interfaces.IJoiningActivity):
	"""Marker interface for 'Leak press release' activity"""
