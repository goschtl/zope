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

class IReviewProcess(eventworkflow.interfaces.IProcess):
	"""A review process"""

class IAcceptResponsibilityActivity(eventworkflow.interfaces.IActivity):
	""" Marker interface for activity"""

class IDecideDraftActivity(eventworkflow.interfaces.IActivity):
	""" Marker interface for activity"""

class IWriteCommentActivity(eventworkflow.interfaces.IActivity):
	""" Marker interface for activity"""
