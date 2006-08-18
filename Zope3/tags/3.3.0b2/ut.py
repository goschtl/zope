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
"""XXX short summary goes here.

XXX longer description goes here.

$Id$
"""
import unittest

__docformat__ = "reStructuredText"

#############################################################################
# If your tests change any global registries, then uncomment the
# following import and include CleanUp as a base class of your
# test. It provides a setUp and tearDown that clear global data that
# has registered with the test cleanup framework.  If your class has
# its own setUp or tearDown, make sure you call the CleanUp setUp and
# tearDown from them, or the benefits of using CleanUp will be lost.
# Don't use CleanUp based tests outside the Zope package.

# from zope.testing.cleanup import CleanUp # Base class w registry cleanup

#############################################################################

class TestSomething(unittest.TestCase):
    def setUp(self):
        # Set up some preconditions
        pass

    def tearDown(self):
        # Clean up after each test
        pass

    def test_something(self):
        # This tests something.  Unittest style guidelines:
        # - never put anything in the test method's docstring, since it makes
        #   it harder to find this test when verbose output is used.  Use a
        #   comment instead.
        # - Call your test method "test_<something>", never
        #   "check_<something>".  The "test" prefix is a unittest default.
        pass


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSomething))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
