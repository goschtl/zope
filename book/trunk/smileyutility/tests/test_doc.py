##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test the workflow ZCML namespace directives.

$Id: test_globalservice.py,v 1.1 2003/08/22 21:27:36 srichter Exp $
"""
import unittest

from zope.interface import Interface
from zope.testing.doctestunit import DocTestSuite

from zope.app.tests import ztapi, placelesssetup

class AbsoluteURL:
    def __init__(self, context, request):
        pass
    def __str__(self):
        return ''

def setUp():
    placelesssetup.setUp()
    ztapi.browserView(Interface, 'absolute_url', AbsoluteURL)


def test_suite():
    return unittest.TestSuite((
        DocTestSuite('book.smileyutility',
                     setUp=setUp, tearDown=placelesssetup.tearDown),
        DocTestSuite('book.smileyutility.globaltheme',
                     setUp=setUp, tearDown=placelesssetup.tearDown),
        DocTestSuite('book.smileyutility.localtheme')
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
