##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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

import unittest
import z3c.layer
import zope.app.testing.functional


layer = zope.app.testing.functional.defineLayer('TestLayer', 'ftesting.zcml')


class ITrustedTestingSkin(z3c.layer.trusted.ITrustedBrowserLayer):
    """The ITrustedBrowserLayer testing skin."""


def test_suite():
    suite = unittest.TestSuite()
    s = zope.app.testing.functional.FunctionalDocFileSuite('README.txt')
    s.layer = TestLayer
    suite.addTest(s)

    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
