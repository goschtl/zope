##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
from zope.app.testing import functional
import doctest
import os
import unittest

ReloadLayer = functional.ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'ReloadLayer', allow_teardown=True)

current_dir = os.path.dirname(__file__)

def openfile(filename, mode='r'):
    return file(os.path.join(current_dir, filename), mode)

def resetFile(test):
    dynamic_orig = openfile('dynamic_orig.py').read()
    openfile('dynamic.py', 'w').write(dynamic_orig)


def test_suite():
    optionflags = (doctest.ELLIPSIS | doctest.REPORT_NDIFF |
                   doctest.NORMALIZE_WHITESPACE |
                   doctest.REPORT_ONLY_FIRST_FAILURE)
    suite = functional.FunctionalDocFileSuite(
        'reload.txt',
        setUp=resetFile, tearDown=resetFile,
        optionflags=optionflags)
    suite.layer = ReloadLayer
    return unittest.TestSuite((
        suite,
        ))
