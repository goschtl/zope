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
"""
$Id: test_dsnparser.py,v 1.2 2002/12/25 14:13:14 jim Exp $
"""
import unittest
from zope.app.rdb import parseDSN


class TestDSNParser(unittest.TestCase):

    def testDBNameOnly(self):
        dsn = 'dbi://test'
        result = {'parameters': {}, 'dbname': 'test', 'username': '',
                  'password': '', 'host': '', 'port': ''}
        self.assertEqual(result, parseDSN(dsn))

    def testDBNameAndParams(self):
        dsn = 'dbi://test;param1=value1;param2=value2'
        result = {'parameters': {'param1': 'value1', 'param2': 'value2'},
                  'dbname': 'test', 'username': '', 'password': '',
                  'host': '', 'port': ''}
        self.assertEqual(result, parseDSN(dsn))

    def testUserPassword(self):
        dsn = 'dbi://mike:muster/test'
        result = {'parameters': {}, 'dbname': 'test', 'username': 'mike',
                  'password': 'muster', 'host': '', 'port': ''}
        self.assertEqual(result, parseDSN(dsn))

    def testUserPasswordAndParams(self):
        dsn = 'dbi://mike:muster/test;param1=value1;param2=value2'
        result = {'parameters': {'param1': 'value1', 'param2': 'value2'},
                  'dbname': 'test', 'username': 'mike', 'password': 'muster',
                  'host': '', 'port': ''}
        self.assertEqual(result, parseDSN(dsn))

    def testAllOptions(self):
        dsn = 'dbi://mike:muster@bohr:5432/test'
        result = {'parameters': {}, 'dbname': 'test', 'username': 'mike',
                  'password': 'muster', 'host': 'bohr', 'port': '5432'}
        self.assertEqual(result, parseDSN(dsn))

    def testAllOptionsAndParams(self):
        dsn = 'dbi://mike:muster@bohr:5432/test;param1=value1;param2=value2'
        result = {'parameters': {'param1': 'value1', 'param2': 'value2'},
                  'dbname': 'test', 'username': 'mike', 'password': 'muster',
                  'host': 'bohr', 'port': '5432'}
        self.assertEqual(result, parseDSN(dsn))

    def testFailures(self):
        self.assertRaises(AssertionError, parseDSN, None)
        self.assertRaises(AssertionError, parseDSN, 'dfi://')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDSNParser))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
