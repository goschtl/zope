##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Unit tests for MySQLDA.

$Id: test_adapter.py,v 1.0 2004/10/10
"""

from unittest import TestCase, TestSuite, main, makeSuite
import MySQLdb

class TestStringConversion(TestCase):
	def test_testStringConversion(self):
		from mysqldbda.adapter import MySQLStringConverter
		converter = MySQLStringConverter('latin-1')
		b =converter('yè yè ü ü ä ä ö ö')
		self.assertEquals(type(b), unicode)
		converter = MySQLStringConverter('utf8')
		b =converter(u'Hi mom!')
		self.assertEquals(type(b),unicode)

def test_suite():
    return TestSuite((
        makeSuite(TestStringConversion),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
