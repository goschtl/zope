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
"""
$Id: test_user.py,v 1.3 2003/05/01 19:35:35 faassen Exp $
"""

from unittest import TestCase, main, makeSuite
from zope.app.services.auth import User

class UserTest(TestCase):

    def setUp(self):
        self._user = User('srichter', 'Stephan Richter',
                          'Local Authentication Service Developer',
                          'srichter', 'hello')

    def testGetLogin(self):
        user = self._user
        self.assertEqual('srichter', user.getLogin())

    def testGetRoles(self):
        user = self._user
        self.assertEqual([], user.getRoles())

    def testValidate(self):
        user = self._user
        self.assertEqual(1, user.validate('hello'))

    def testGetId(self):
        user = self._user
        self.assertEqual('srichter', user.getId())

    def testGetTitle(self):
        user = self._user
        self.assertEqual('Stephan Richter', user.getTitle())

    def testGetDescription(self):
        user = self._user
        self.assertEqual('Local Authentication Service Developer',
                         user.getDescription())

    def testSetTitle(self):
        user = self._user
        user.setTitle('Stephan 2')
        self.assertEqual('Stephan 2', user.getTitle())

    def testSetDescription(self):
        user = self._user
        user.setDescription('Programmer')
        self.assertEqual('Programmer', user.getDescription())

    def testSetLogin(self):
        user = self._user
        user.setLogin('srichter2')
        self.assertEqual('srichter', user.getLogin())

    def testSetRoles(self):
        # XXX Needs a test
        user = self._user

    def testSetPassword(self):
        user = self._user
        user.setPassword('hello2')
        self.assertEqual(1, user.validate('hello2'))


def test_suite():
    return makeSuite(UserTest)

if __name__=='__main__':
    main(defaultTest='test_suite')
