##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Search Filter Tests

$Id$
"""
__docformat__ = "reStructuredText"
import unittest
from zope.app.testing import setup
from zope.testing import doctest
from zope.testing.doctestunit import DocFileSuite
from zope.testing.doctestunit import DocTestSuite
from zope.testing.doctestunit import pprint

def test_suite():
    return unittest.TestSuite((
        DocFileSuite('README.txt',
                     setUp=setup.placefulSetUp,
                     tearDown=setup.placefulTearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

