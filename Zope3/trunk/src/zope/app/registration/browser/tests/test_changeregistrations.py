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
"""Registration Change Tests

$Id: test_changeregistrations.py,v 1.1 2004/03/13 18:01:18 srichter Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.publisher.browser import TestRequest
from zope.app.registration.tests.registrationstack \
     import TestingRegistrationStack
from zope.app.registration.browser import ChangeRegistrations

class Test(TestCase):

    def test_applyUpdates_and_setPrefix(self):
        registry = TestingRegistrationStack('a', 'b', 'c')
        request = TestRequest()
        view = ChangeRegistrations(registry, request)
        view.setPrefix("Pigs")

        # Make sure we don't apply updates unless asked to
        request.form = {'Pigs.active': 'disable'}
        view.applyUpdates()
        self.assertEqual(registry._data, ('a', 'b', 'c'))

        # Now test disabling
        request.form = {'submit_update': '', 'Pigs.active': 'disable'}
        view.applyUpdates()
        self.assertEqual(registry._data, (None, 'a', 'b', 'c'))

        # Now test enabling c
        request.form = {'submit_update': '', 'Pigs.active': 'c'}
        view.applyUpdates()
        self.assertEqual(registry._data, ('c', 'a', 'b'))


def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
