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
"""Tests the zope policy.

$Id: test_zopepolicy.py 73662 2007-03-27 06:52:40Z dobe $
"""

import unittest, doctest
from zope.testing import module
from zope.testing.doctestunit import DocFileSuite, DocTestSuite
from zope.app.testing import placelesssetup, ztapi, functional, setup
from z3c.securitytool import testing

def test_suite():
    flags =  doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
  
    functionalTest = functional.FunctionalDocFileSuite(
        'README.txt',optionflags=flags,globs={'lets': 'test'},
        tearDown=placelesssetup.tearDown)

    functionalTest.layer = testing.SecurityToolLayer

    return unittest.TestSuite((
        #unitTest,
        functionalTest,))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

