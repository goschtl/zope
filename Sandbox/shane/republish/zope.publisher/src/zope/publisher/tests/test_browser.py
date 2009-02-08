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
"""Test zope.publisher.browser doctests

$Id$
"""
import unittest
from zope.testing.doctestunit import DocTestSuite

__docformat__ = "reStructuredText"

from zope.component.testing import PlacelessSetup as CAPlacelessSetup
from zope.component.eventtesting import PlacelessSetup as EventPlacelessSetup
from zope.i18n.testing import PlacelessSetup as I18nPlacelessSetup
from zope.security.management import newInteraction

class PlacelessSetup(CAPlacelessSetup,
                     EventPlacelessSetup,
                     I18nPlacelessSetup):

    def setUp(self, doctesttest=None):
        CAPlacelessSetup.setUp(self)
        EventPlacelessSetup.setUp(self)
        I18nPlacelessSetup.setUp(self)
        newInteraction()

    def tearDown_(self, doctesttest=None):
        self.tearDown()

ps = PlacelessSetup()

def test_suite():
    return unittest.TestSuite((
        DocTestSuite('zope.publisher.browser',
                     setUp=ps.setUp,
                     tearDown=ps.tearDown_),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
