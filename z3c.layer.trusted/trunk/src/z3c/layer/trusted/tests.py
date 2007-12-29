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
import re
import unittest
from zope.testing import renormalizing
from zope.app.testing import functional

from z3c.layer import trusted

layer = functional.defineLayer('TestLayer', 'ftesting.zcml')


class ITrustedTestingSkin(trusted.ITrustedBrowserLayer):
    """The ITrustedBrowserLayer testing skin."""


def getRootFolder():
    return functional.FunctionalTestSetup().getRootFolder()


def test_suite():
    suite = unittest.TestSuite()

    s = functional.FunctionalDocFileSuite(
        'README.txt',
        globs={'getRootFolder': getRootFolder},
        checker = renormalizing.RENormalizing([
            (re.compile(r'httperror_seek_wrapper:', re.M), 'HTTPError:'),
            ])
        )
    s.layer = TestLayer
    suite.addTest(s)

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
