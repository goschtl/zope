##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Pluggable Auth Browser Tests

$Id: test_authentication.py 25177 2004-06-02 13:17:31Z jim $
"""
from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.pluggableauth.browser.authentication import \
    PrincipalAuthenticationView
from zope.app.pluggableauth.tests.authsetup import AuthSetup



class PrincipalAuthenticationViewTest(AuthSetup, TestCase):

    def test_authenticate(self):
        request = self.getRequest('srichter', 'hello')
        view = PrincipalAuthenticationView(self._one, request)
        self.assertEqual(self._srichter, view.authenticate())


def test_suite():
    t1 = makeSuite(PrincipalAuthenticationViewTest)
    return TestSuite((t1,))


if __name__=='__main__':
    main(defaultTest='test_suite')

