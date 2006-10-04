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
import unittest
from zope.app.testing import placelesssetup
from zope.testing.doctestunit import DocFileSuite

def test_suite():

    stressSuite = DocFileSuite(
        'stresstest.txt',
        setUp=placelesssetup.setUp, tearDown=placelesssetup.tearDown,
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    stressSuite.level = 2

    return unittest.TestSuite(
        (
        DocFileSuite('README.txt',
                     setUp=placelesssetup.setUp,
                     tearDown=placelesssetup.tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('index.txt',),
        stressSuite
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
