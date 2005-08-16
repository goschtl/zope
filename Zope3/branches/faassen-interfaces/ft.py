##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: ft.py,v 1.2 2004/04/06 20:57:58 jim Exp $
"""

import unittest
from zope.app.tests.functional import FunctionalTestCase

# If you are writing a functional test that simulates browser requests, use
# BrowserTestCase instead of FunctionalTestCase

# Functional tests should not change any global registries (or if they do, they
# should clean up after themselves).

class TestSomething(FunctionalTestCase):

    def setUp(self):
        FunctionalTestCase.setUp(self)
        # Set up some preconditions
        #
        # You are guaranteed to have an empty root folder (accessible by
        # calling self.getRootFolder()), all global services and basic local
        # services set up.
        #
        # If you add something to the root folder or in general change
        # anything in the ZODB, you might need to perform a
        #   from zope.transaction import get_transaction
        #   get_transaction().commit()
        # for those changes to become visible to the publisher.

    def tearDown(self):
        # Clean up after each test
        #
        # You do not need to clean up the ZODB.  That will be done
        # automatically by FunctionalTestCase.tearDown().
        FunctionalTestCase.tearDown(self)

    def test_something(self):
        # This tests something.  Unittest style guidelines:
        # - never put anything in the test method's docstring, since it makes
        #   it harder to find this test when verbose output is used.  Use a
        #   comment instead.
        # - Call your test method "test_<something>", never
        #   "check_<something>".  The "test" prefix is a unittest default.
        #
        # There are helper methods in FunctionalTestCase and BrowserTestCase
        # for accessing the ZODB and emulating publication requests.  See the
        # docstrings in zope.app.tests.functional module.
        pass


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSomething))
    return suite


if __name__ == '__main__':
    unittest.main()
