##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Run all unit tests

To run all tests, invoke this script with the PYTHONPATH environment
variable set.  Example:

PYTHONPATH=~/cvs/Zope/lib/python python testAll.py

$Id$
"""

import sys, unittest

try:
    import apelib
except ImportError:
    # The Ape product makes apelib available as a top-level package.
    import ZODB
    import Products.Ape
    import apelib

from testserialization import SerializationTests
from testimpl import ApelibImplTests
from teststorage import ApeStorageTests
from testio import ApeIOTests
from testzope2fs import Zope2FSTests, Zope2FSUnderscoreTests
from testparams import ParamsTests
from testsqlimpl import ApelibSQLImplTests
from testzodbtables import ZODBTableTests, ZODBTableTestsWithoutPrimaryKey
from testscanner import ScanControlTests, ScannerTests
from testzope2sql import PsycopgTests, MySQLTests
import testzope2sql


sql_suite = testzope2sql.test_suite()

def test_suite():
    suite = unittest.TestSuite()
    for klass in (
        SerializationTests,
        ZODBTableTests,
        ZODBTableTestsWithoutPrimaryKey,
        ApelibImplTests,
        ApeStorageTests,
        ApeIOTests,
        Zope2FSTests,
        Zope2FSUnderscoreTests,
        ParamsTests,
        ApelibSQLImplTests,
        ScanControlTests,
        ScannerTests,
        ):
        suite.addTest(unittest.makeSuite(klass, 'test'))
    suite.addTest(sql_suite)
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

