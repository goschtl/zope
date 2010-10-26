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
"""z3c.form Test Module

$Id: test_doc.py 77114 2007-06-26 22:35:05Z srichter $
"""
__docformat__ = "reStructuredText"

import re
import unittest
from zope.testing import renormalizing
from zope.app.testing import functional
import doctest
import z3c.layer.ready2go

layer = functional.defineLayer('TestLayer', 'ftesting.zcml')


def getRootFolder():
    return functional.FunctionalTestSetup().getRootFolder()


def test_suite():
    suite = unittest.TestSuite()

    s = functional.FunctionalDocFileSuite(
        'README.txt',
        globs={'getRootFolder': getRootFolder},
        optionflags=doctest.NORMALIZE_WHITESPACE,
        checker = renormalizing.RENormalizing([
            (re.compile(r'httperror_seek_wrapper:', re.M), 'HTTPError:'),
            ])
        )
    s.layer = TestLayer
    suite.addTest(s)

    return suite
