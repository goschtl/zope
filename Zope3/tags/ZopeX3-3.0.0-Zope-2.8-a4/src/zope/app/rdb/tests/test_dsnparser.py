##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""DSN Parser tests

$Id$
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

    def testPasswordWithColon(self):
        dsn = 'dbi://mike:before:after/test'
        result = {'parameters': {}, 'dbname': 'test', 'username': 'mike',
                  'password': 'before:after', 'host': '', 'port': ''}
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
        self.assertRaises(ValueError, parseDSN, None)
        self.assertRaises(ValueError, parseDSN, 'dfi://')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDSNParser))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
