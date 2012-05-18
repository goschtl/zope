##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""
$Id$
"""
__docformat__="restructuredtext"

import unittest

import twisted.trial.unittest

class TestTrialBrokenSetup(twisted.trial.unittest.TestCase):

    def setUp(self):
        raise Exception("broken setup")

    def tearDown(self):
        pass

    def test_error(self):
        raise Exception("this test is a broken trial test :-)")

    def test_failure(self):
        self.assert_(False, "I am a failed trial test")

    def test_assert_ok(self):
        self.assert_(True, "I am a good test")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestTrialBrokenSetup))

    return suite

if __name__ == '__main__':
    test_suite()
