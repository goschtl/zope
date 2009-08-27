##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Browser Menu Item Tests

$Id: test_menu.py 29570 2005-03-18 22:53:37Z rogerineichen $
"""
import unittest
from zope.testing import doctest, cleanup, doctestunit

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('../menu.txt',
                             setUp=lambda test:cleanup.setUp(),
                             tearDown=lambda test:cleanup.tearDown(),
                             globs={'pprint': doctestunit.pprint},
                             optionflags=doctest.NORMALIZE_WHITESPACE),
        ))
