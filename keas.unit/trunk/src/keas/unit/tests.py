##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
import doctest
from zope.testing.doctestunit import DocFileSuite

# set up internationalization
import zope.i18nmessageid
_ = zope.i18nmessageid.MessageFactory("keas.com")

def test_suite():
    return unittest.TestSuite((
        DocFileSuite(
            'README.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))
