##############################################################################
#
# Copyright (c) 2003 Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""

$Id: $
"""
import os
import unittest

import zope
from zope.app.tests import placelesssetup
from zope.configuration import xmlconfig
from zope.app.tests import ztapi
import zope.app.annotation.interfaces
import zope.app.annotation.attribute
from zope.testing import module

def zcml(s):
    context = xmlconfig.file('meta.zcml', package=zope.app.wfmc)
    xmlconfig.string(s, context)

def setUp(test):
    test.globs['this_directory'] = os.path.dirname(__file__)
    placelesssetup.setUp(test)

def test_suite():
    from zope.testing import doctest
    return doctest.DocFileSuite(
                'zcml.txt', globs={'zcml': zcml},
                setUp=setUp,
                tearDown=placelesssetup.tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE,
           )

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

