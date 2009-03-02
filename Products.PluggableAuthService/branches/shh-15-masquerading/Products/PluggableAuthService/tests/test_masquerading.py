##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors. All Rights
# Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this
# distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import unittest

from Products.PluggableAuthService.tests import pastc

from Products.PluggableAuthService.interfaces.plugins import IExtractionPlugin
from Products.PluggableAuthService.utils import splitmasq
from Products.PluggableAuthService.utils import joinmasq

from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.Permissions import view as View


class SplitMasqTests(unittest.TestCase):

    def testSimpleId(self):
        self.assertEqual(splitmasq('fred'), ('fred', None))

    def testMasqueradingId(self):
        self.assertEqual(splitmasq('fred/wilma'), ('fred', 'wilma'))

    def testStartsWithSlash(self):
        self.assertEqual(splitmasq('/fred'), ('/fred', None))

    def testEndsWithSlash(self):
        self.assertEqual(splitmasq('fred/'), ('fred/', None))

    def testSpuriousSlash(self):
        self.assertEqual(splitmasq('fred//wilma'), ('fred', '/wilma'))

    def testSpuriousId(self):
        self.assertEqual(splitmasq('fred/wilma/pebbles'), ('fred', 'wilma/pebbles'))

    def testNoneId(self):
        self.assertEqual(splitmasq(None), (None, None))

    def testEmptyId(self):
        self.assertEqual(splitmasq(''), ('', None))


class JoinMasqTests(unittest.TestCase):

    def testSimpleIds(self):
        self.assertEqual(joinmasq('barney', 'betty'), 'barney/betty')

    def testFirstIdNone(self):
        self.assertEqual(joinmasq(None, 'betty'), None)

    def testSecondIdNone(self):
        self.assertEqual(joinmasq('barney', None), 'barney')

    def testBothIdsNone(self):
        self.assertEqual(joinmasq(None, None), None)

    def testFirstIdEmpty(self):
        self.assertEqual(joinmasq('', 'betty'), '')

    def testSecondIdEmpty(self):
        self.assertEqual(joinmasq('barney', ''), 'barney')

    def testBothIdsEmpty(self):
        self.assertEqual(joinmasq('', ''), '')


class MasqueradingTests(pastc.PASTestCase):

    def afterSetUp(self):
        self.pas = self.folder.acl_users
        # Create a masquerading user
        self.pas.users.addUser('fred', 'fred', 'r0ck')
        self.pas.roles.assignRoleToPrincipal('Manager', 'fred')
        # Create a masqueraded user
        self.pas.users.addUser('wilma', 'wilma', 'geheim')
        self.pas.roles.assignRoleToPrincipal(pastc.user_role, 'wilma')
        # Create a protected document
        self.folder.manage_addDTMLMethod('doc', file='the document')
        self.doc = self.folder.doc
        self.doc.manage_permission(View, [pastc.user_role], acquire=False)
        # Start out as Anonymous User
        self.logout()

    def test__extractUserIds(self):
        request = self.app.REQUEST
        request._auth = 'Basic %s' % pastc.mkauth('fred/wilma', 'r0ck')

        user_id, info = self.pas._extractUserIds(request, self.pas.plugins)[0]
        self.assertEqual(user_id, 'fred/wilma')
        self.assertEqual(info, 'fred/wilma')

    def test__findUser(self):
        # User decoration does not find the real user name but uses the
        # passed-in value. This is ok as PAS always passes a useful name.
        user = self.pas._findUser(self.pas.plugins, 'fred/wilma', 'SomeValue')
        self.assertEqual(user.getId(), 'wilma')
        self.assertEqual(user.getUserName(), 'SomeValue')
        self.assertEqual(user.getRoles(), ['Authenticated', pastc.user_role])

    def test__findUser_masquerading_denied(self):
        user = self.pas._findUser(self.pas.plugins, 'wilma/fred')
        self.assertEqual(user, None)

    def test__verifyUser_by_login(self):
        info = self.pas._verifyUser(self.pas.plugins, login='fred/wilma')
        self.assertEqual(info['id'], 'wilma')
        self.assertEqual(info['login'], 'wilma')

    def test__verifyUser_by_id(self):
        info = self.pas._verifyUser(self.pas.plugins, user_id='fred/wilma')
        self.assertEqual(info['id'], 'wilma')
        self.assertEqual(info['login'], 'wilma')

    def test_getUser(self):
        user = self.pas.getUser('fred/wilma')
        self.assertEqual(user.getId(), 'wilma')
        self.assertEqual(user.getUserName(), 'wilma')
        self.assertEqual(user.getRoles(), ['Authenticated', pastc.user_role])

    def test_getUserById(self):
        user = self.pas.getUserById('fred/wilma')
        self.assertEqual(user.getId(), 'wilma')
        self.assertEqual(user.getUserName(), 'wilma')
        self.assertEqual(user.getRoles(), ['Authenticated', pastc.user_role])

    def test_validate(self):
        # Rig the request so it looks like we traversed to doc
        request = self.app.REQUEST
        request['PUBLISHED'] = self.doc
        request['PARENTS'] = [self.folder, self.app]
        request.steps = list(self.doc.getPhysicalPath())
        request._auth = 'Basic %s' % pastc.mkauth('fred/wilma', 'r0ck')

        user = self.pas.validate(request)
        self.failIf(user is None)
        self.assertEqual(user.getId(), 'wilma')
        self.assertEqual(user.getUserName(), 'wilma')
        self.assertEqual(user.getRoles(), ['Authenticated', pastc.user_role])

        user = getSecurityManager().getUser()
        self.failIf(user is None)
        self.assertEqual(user.getId(), 'wilma')
        self.assertEqual(user.getUserName(), 'wilma')
        self.assertEqual(user.getRoles(), ['Authenticated', pastc.user_role])

    def test_validate_masquerading_denied(self):
        # Rig the request so it looks like we traversed to doc
        request = self.app.REQUEST
        request['PUBLISHED'] = self.doc
        request['PARENTS'] = [self.folder, self.app]
        request.steps = list(self.doc.getPhysicalPath())
        request._auth = 'Basic %s' % pastc.mkauth('wilma/fred', 'geheim')

        user = self.pas.validate(request)
        self.assertEqual(user, None)

        user = getSecurityManager().getUser()
        self.failIf(user is None)
        self.assertEqual(user.getId(), None)
        self.assertEqual(user.getUserName(), 'Anonymous User')
        self.assertEqual(user.getRoles(), ('Anonymous',))


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(SplitMasqTests),
        unittest.makeSuite(JoinMasqTests),
        unittest.makeSuite(MasqueradingTests),
    ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

