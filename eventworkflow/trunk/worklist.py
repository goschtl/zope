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
from interfaces import IWorklistUtility

class BasicWorklistUtility:
	"""A simple worklist utility"""
	zope.interface.implements(IWorklistUtility)

	def __init__(self):
		self.items = []
		
	def addWorkitem(self, item):
		self.items.append(item)

	def itemsFor(self, pid):
		"""Return all wokitems for principal"""

		#XXX groups support
		return [x for x in self.items if pid in x.principals]
