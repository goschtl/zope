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
import eventworkflow.worklist
from zope.testing.doctest import DocTestSuite

def testService(test):
	"""
	>>> wl = eventworkflow.worklist.BasicWorklistUtility()
	>>> wl.itemsFor('foo')
	[]

	Define a some work items

	>>> class FakeWorkItem:
	...   def __init__(self, principals=[], name=''):
	...     self.principals = principals
	...     self.name = name

	>>> foo = FakeWorkItem(['thomas', 'peter'], 'Learn Zope 3')
	>>> bar = FakeWorkItem(['thomas'], 'Find Zope 3 Zen')
	>>> wl.addWorkitem(foo)
	>>> wl.addWorkitem(bar)

	>>> wl.itemsFor('foo')
	[]
	>>> [x.name for x in wl.itemsFor('peter')]
	['Learn Zope 3']
	>>> [x.name for x in wl.itemsFor('thomas')]
	['Learn Zope 3', 'Find Zope 3 Zen']
	"""

def test_suite():
	return DocTestSuite()
