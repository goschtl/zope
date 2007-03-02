##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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
"""Tag test setup

$Id$
"""
__docformat__ = "reStructuredText"
import doctest
import os
import unittest
import zope.component
from zope.testing.doctestunit import DocFileSuite
from zope.app.keyreference import testing
from zope.app.testing import placelesssetup

dirpath = os.path.dirname(__file__)

def setUp(test):
    placelesssetup.setUp(test)
    zope.component.provideAdapter(testing.SimpleKeyReference)

def test_suite():
    return unittest.TestSuite((
        DocFileSuite(
            'README.txt',
            globs={'dirpath': dirpath},
            setUp=setUp, tearDown=placelesssetup.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
