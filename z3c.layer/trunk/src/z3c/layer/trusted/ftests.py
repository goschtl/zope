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
from zope.app.testing import functional

from z3c.layer import trusted


class ITrustedTestingSkin(trusted.ITrustedBrowserLayer):
    """The ITrustedBrowserLayer testing skin."""


def getRootFolder():
    return functional.FunctionalTestSetup().getRootFolder()


def test_suite():
    suite = unittest.TestSuite((
        functional.FunctionalDocFileSuite('README.txt',
            globs={'getRootFolder': getRootFolder}),
        ))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
