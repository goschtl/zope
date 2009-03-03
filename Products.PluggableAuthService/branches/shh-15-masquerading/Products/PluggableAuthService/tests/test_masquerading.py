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
import os

from Products.PluggableAuthService.tests import pastc

from Products.PluggableAuthService.interfaces.plugins import IExtractionPlugin
from Products.PluggableAuthService.utils import masquerading
from Products.PluggableAuthService.utils import splitmasq

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


class MasqueradingTests(pastc.PASTestCase):

    def afterSetUp(self):
        self.pas = self.folder.acl_users
        # Create a masquerading user (Manager)
        self.pas.users.addUser('fred_id', 'fred', 'r0ck')
        self.pas.roles.assignRoleToPrincipal('Manager', 'fred_id')
        # Create a masquerading user (Masquerader)
        self.pas.users.addUser('barney_id', 'barney', 'p4per')
        self.pas.roles.addRole('Masquerader')
        self.pas.roles.assignRoleToPrincipal('Masquerader', 'barney_id')
        # Create a masqueraded user
        self.pas.users.addUser('wilma_id', 'wilma', 'geheim')
        self.pas.roles.assignRoleToPrincipal(pastc.user_role, 'wilma_id')
        # Create a protected document
        self.folder.manage_addDTMLMethod('doc', file='the document')
        self.doc = self.folder.doc
        self.doc.manage_permission(View, [pastc.user_role], acquire=False)
        # Start out as Anonymous User
        self.logout()
        # Enable masquerading
        masquerading(True)

    def afterClear(self):
        # Disable masquerading
        masquerading(False)

    def test__extractUserIds_Manager(self):
        request = self.app.REQUEST
        request._auth = 'Basic %s' % pastc.mkauth('fred/wilma', 'r0ck')

        uids = self.pas._extractUserIds(request, self.pas.plugins)
        self.assertEqual(len(uids), 1)

        user_id, info = uids[0]
        self.assertEqual(user_id, 'wilma_id')
        self.assertEqual(info, 'wilma')

    def test__extractUserIds_Masquerader(self):
        request = self.app.REQUEST
        request._auth = 'Basic %s' % pastc.mkauth('barney/wilma', 'p4per')

        uids = self.pas._extractUserIds(request, self.pas.plugins)
        self.assertEqual(len(uids), 1)

        user_id, info = uids[0]
        self.assertEqual(user_id, 'wilma_id')
        self.assertEqual(info, 'wilma')

    def test__extractUserIds_masquerading_disabled(self):
        request = self.app.REQUEST
        request._auth = 'Basic %s' % pastc.mkauth('fred/wilma', 'r0ck')

        masquerading(False)

        uids = self.pas._extractUserIds(request, self.pas.plugins)
        self.assertEqual(len(uids), 0)

    def test__extractUserIds_masquerading_denied(self):
        request = self.app.REQUEST
        request._auth = 'Basic %s' % pastc.mkauth('wilma/fred', 'geheim')

        uids = self.pas._extractUserIds(request, self.pas.plugins)
        self.assertEqual(len(uids), 0)

    def test__extractUserIds_bad_role_user(self):
        request = self.app.REQUEST
        request._auth = 'Basic %s' % pastc.mkauth('fred/betty', 'r0ck')

        uids = self.pas._extractUserIds(request, self.pas.plugins)
        self.assertEqual(len(uids), 0)

    def test__verifyUser_by_id(self):
        info = self.pas._verifyUser(self.pas.plugins, user_id='fred_id/wilma_id')
        self.assertEqual(info['id'], 'wilma_id')
        self.assertEqual(info['login'], 'wilma')

    def test__verifyUser_by_login(self):
        info = self.pas._verifyUser(self.pas.plugins, login='fred/wilma')
        self.assertEqual(info['id'], 'wilma_id')
        self.assertEqual(info['login'], 'wilma')

    def test__verifyUser_bad_role_user(self):
        info = self.pas._verifyUser(self.pas.plugins, login='fred/betty')
        self.assertEqual(info, None)

    def test_validate_Manager(self):
        # Rig the request so it looks like we traversed to doc
        request = self.app.REQUEST
        request['PUBLISHED'] = self.doc
        request['PARENTS'] = [self.folder, self.app]
        request.steps = list(self.doc.getPhysicalPath())
        request._auth = 'Basic %s' % pastc.mkauth('fred/wilma', 'r0ck')

        user = self.pas.validate(request)
        self.failIfEqual(user, None)
        self.assertEqual(user.getId(), 'wilma_id')
        self.assertEqual(user.getUserName(), 'wilma')
        self.assertEqual(user.getRoles(), ['Authenticated', pastc.user_role])

        user = getSecurityManager().getUser()
        self.failIfEqual(user, None)
        self.assertEqual(user.getId(), 'wilma_id')
        self.assertEqual(user.getUserName(), 'wilma')
        self.assertEqual(user.getRoles(), ['Authenticated', pastc.user_role])

    def test_validate_Masquerader(self):
        # Rig the request so it looks like we traversed to doc
        request = self.app.REQUEST
        request['PUBLISHED'] = self.doc
        request['PARENTS'] = [self.folder, self.app]
        request.steps = list(self.doc.getPhysicalPath())
        request._auth = 'Basic %s' % pastc.mkauth('barney/wilma', 'p4per')

        user = self.pas.validate(request)
        self.failIfEqual(user, None)
        self.assertEqual(user.getId(), 'wilma_id')
        self.assertEqual(user.getUserName(), 'wilma')
        self.assertEqual(user.getRoles(), ['Authenticated', pastc.user_role])

        user = getSecurityManager().getUser()
        self.failIfEqual(user, None)
        self.assertEqual(user.getId(), 'wilma_id')
        self.assertEqual(user.getUserName(), 'wilma')
        self.assertEqual(user.getRoles(), ['Authenticated', pastc.user_role])

    def test_validate_masquerading_disabled(self):
        # Rig the request so it looks like we traversed to doc
        request = self.app.REQUEST
        request['PUBLISHED'] = self.doc
        request['PARENTS'] = [self.folder, self.app]
        request.steps = list(self.doc.getPhysicalPath())
        request._auth = 'Basic %s' % pastc.mkauth('fred/wilma', 'r0ck')

        masquerading(False)

        user = self.pas.validate(request)
        self.assertEqual(user, None)

        user = getSecurityManager().getUser()
        self.failIfEqual(user, None)
        self.assertEqual(user.getId(), None)
        self.assertEqual(user.getUserName(), 'Anonymous User')
        self.assertEqual(user.getRoles(), ('Anonymous',))

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
        self.failIfEqual(user, None)
        self.assertEqual(user.getId(), None)
        self.assertEqual(user.getUserName(), 'Anonymous User')
        self.assertEqual(user.getRoles(), ('Anonymous',))

    def test_validate_bad_role_user(self):
        # Rig the request so it looks like we traversed to doc
        request = self.app.REQUEST
        request['PUBLISHED'] = self.doc
        request['PARENTS'] = [self.folder, self.app]
        request.steps = list(self.doc.getPhysicalPath())
        request._auth = 'Basic %s' % pastc.mkauth('fred/betty', 'r0ck')

        user = self.pas.validate(request)
        self.assertEqual(user, None)

        user = getSecurityManager().getUser()
        self.failIfEqual(user, None)
        self.assertEqual(user.getId(), None)
        self.assertEqual(user.getUserName(), 'Anonymous User')
        self.assertEqual(user.getRoles(), ('Anonymous',))


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(SplitMasqTests),
        unittest.makeSuite(MasqueradingTests),
    ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

