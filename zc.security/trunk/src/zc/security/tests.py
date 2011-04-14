##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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
$Id$
"""
import unittest

from zope.testing import doctest
from zope.app.testing import placelesssetup

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'search.txt',
            setUp=placelesssetup.setUp,
            tearDown=placelesssetup.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS,
           ),
       ))
