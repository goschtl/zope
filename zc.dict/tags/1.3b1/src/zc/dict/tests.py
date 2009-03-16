##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""Tests for zc.dict

$Id$
"""
import unittest
from zope.testing import doctest


optionflags = (doctest.INTERPRET_FOOTNOTES |
               doctest.REPORT_NDIFF |
               doctest.ELLIPSIS)


def test_suite():
    return unittest.TestSuite([
        doctest.DocFileSuite('dict.txt', 'ordered.txt',
                             optionflags=optionflags),
        ])


def test_suite_generations():
    suite = test_suite()
    suite.addTest(doctest.DocFileSuite('generations/evolve1.txt',
                                       optionflags=optionflags))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
