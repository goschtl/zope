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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: test_changeconfigurations.py,v 1.2 2002/12/25 14:12:38 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.publisher.browser import TestRequest
from zope.app.services.tests.configurationregistry \
     import TestingConfigurationRegistry

class Test(TestCase):

    def test_applyUpdates_and_setPrefix(self):
        registry = TestingConfigurationRegistry('a', 'b', 'c')
        request = TestRequest()
        from zope.app.browser.services.changeconfigurations \
             import ChangeConfigurations
        view = ChangeConfigurations(registry, request)
        view.setPrefix("Roles")

        # Make sure we don't apply updates unless asked to
        request.form = {'Roles.active': 'disable'}
        view.applyUpdates()
        self.assertEqual(registry._data, ('a', 'b', 'c'))

        # Now test disabling
        request.form = {'submit_update': '', 'Roles.active': 'disable'}
        view.applyUpdates()
        self.assertEqual(registry._data, (None, 'a', 'b', 'c'))

        # Now test enabling c
        request.form = {'submit_update': '', 'Roles.active': 'c'}
        view.applyUpdates()
        self.assertEqual(registry._data, ('c', 'a', 'b'))



def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
