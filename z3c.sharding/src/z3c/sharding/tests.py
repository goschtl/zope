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
"""Test Setup.

$Id: tests.py 165 2008-03-12 00:09:25Z pcardune $
"""
import unittest
from zope.testing import doctestunit, doctest
#from zope.app.testing import placelesssetup

# set up internationalization
#import zope.i18nmessageid
#_ = zope.i18nmessageid.MessageFactory("zope")

def test_suite():
    return unittest.TestSuite((
        doctestunit.DocFileSuite(
            'README.txt',
            #'implementation.txt',
            #setUp=placelesssetup.setUp, tearDown=placelesssetup.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
