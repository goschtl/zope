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
"""
$Id$
"""
__docformat__ = "reStructuredText"
import os
import unittest
from zope.app.testing import functional
from z3c.formdemo import testing

def getRootFolder():
    return functional.FunctionalTestSetup().getRootFolder()

def test_suite():
    suites = []
    for docpath in (('message', 'README.txt'),
                    ('widgets', 'README.txt'),
                    ('questionnaire', 'README.txt'),
                    ('calculator', 'README.txt'),
                    ('wizard', 'README.txt'),
                    ('spreadsheet', 'README.txt'),
                    ('addressbook', 'README.txt'),
                    ('sqlmessage', 'README.txt'),
                    ):
        suite = functional.FunctionalDocFileSuite(
            os.path.join(*docpath),
            setUp=testing.setUp,
            globs={'getRootFolder': getRootFolder})
        suite.layer = testing.FormDemoLayer
        suites.append(suite)
    return unittest.TestSuite(suites)


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
