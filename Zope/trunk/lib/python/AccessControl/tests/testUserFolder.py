##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""User folder tests
"""

__rcs_id__='$Id: testUserFolder.py,v 1.8 2004/01/30 14:00:32 shh Exp $'
__version__='$Revision: 1.8 $'[11:-2]

import os, sys, base64, unittest

from Testing.makerequest import makerequest

import Zope
Zope.startup()

from AccessControl import Unauthorized
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl.User import BasicUserFolder
from AccessControl.User import User

# XXX: Uncomment to enforce C implementation
#from AccessControl.SecurityManager import setSecurityPolicy
#from AccessControl.cAccessControl import ZopeSecurityPolicy
#setSecurityPolicy(ZopeSecurityPolicy(True, True))


class UserFolderTests(unittest.TestCase):

    def setUp(self):
        get_transaction().begin()
        self.app = makerequest(Zope.app())
        try:
            # Set up a user and role
            self.uf = self.app.acl_users    
            self.uf._doAddUser('user1', 'secret', ['role1'], [])
            self.app._addRole('role1')
            self.app.manage_role('role1', ['View'])
            # Set up a published object accessible to user
            self.app.addDTMLMethod('doc', file='')
            self.app.doc.manage_permission('View', ['role1'], acquire=0)
            # Rig the REQUEST so it looks like we traversed to doc
            self.app.REQUEST.set('PUBLISHED', self.app.doc)
            self.app.REQUEST.set('PARENTS', [self.app])
            self.app.REQUEST.steps = ['doc']
            self.basic = 'Basic %s' % base64.encodestring('user1:secret')
        except:
            self.tearDown()
            raise

    def tearDown(self):
        noSecurityManager()
        get_transaction().abort()
        self.app._p_jar.close()

    def login(self, name):
        user = self.uf.getUserById(name)
        user = user.__of__(self.uf)
        newSecurityManager(None, user)

    def testGetUser(self):
        self.failIfEqual(self.uf.getUser('user1'), None)

    def testGetBadUser(self):
        self.assertEqual(self.uf.getUser('user2'), None)

    def testGetUserById(self):
        self.failIfEqual(self.uf.getUserById('user1'), None)

    def testGetBadUserById(self):
        self.assertEqual(self.uf.getUserById('user2'), None)

    def testGetUsers(self):
        users = self.uf.getUsers()
        self.failUnless(users)
        self.assertEqual(users[0].getUserName(), 'user1')

    def testGetUserNames(self):
        names = self.uf.getUserNames()
        self.failUnless(names)
        self.assertEqual(names[0], 'user1')

    def testIdentify(self):
        name, password = self.uf.identify(self.basic)
        self.assertEqual(name, 'user1')
        self.assertEqual(password, 'secret')

    def testGetRoles(self):
        user = self.uf.getUser('user1')
        self.failUnless('role1' in user.getRoles())

    def testGetRolesInContext(self):
        user = self.uf.getUser('user1')
        self.app.manage_addLocalRoles('user1', ['Owner'])
        roles = user.getRolesInContext(self.app)
        self.failUnless('role1' in roles)
        self.failUnless('Owner' in roles)

    def testHasRole(self):
        user = self.uf.getUser('user1')
        self.failUnless(user.has_role('role1', self.app))

    def testHasLocalRole(self):
        user = self.uf.getUser('user1')
        self.app.manage_addLocalRoles('user1', ['Owner'])
        self.failUnless(user.has_role('Owner', self.app))

    def testHasPermission(self):
        user = self.uf.getUser('user1')
        self.failUnless(user.has_permission('View', self.app))
        self.app.manage_role('role1', ['Add Folders'])
        self.failUnless(user.has_permission('Add Folders', self.app))

    def testHasLocalRolePermission(self):
        user = self.uf.getUser('user1')
        self.app.manage_role('Owner', ['Add Folders'])
        self.app.manage_addLocalRoles('user1', ['Owner'])
        self.failUnless(user.has_permission('Add Folders', self.app))
        
    def testAuthenticate(self):
        user = self.uf.getUser('user1')
        self.failUnless(user.authenticate('secret', self.app.REQUEST))

    def testValidate(self):
        user = self.uf.validate(self.app.REQUEST, self.basic, ['role1'])
        self.failIfEqual(user, None)
        self.assertEqual(user.getUserName(), 'user1')

    def testNotValidateWithoutAuth(self):
        user = self.uf.validate(self.app.REQUEST, '', ['role1'])
        self.assertEqual(user, None)

    def testNotValidateWithoutRoles(self):
        user = self.uf.validate(self.app.REQUEST, self.basic)
        self.assertEqual(user, None)

    def testNotValidateWithEmptyRoles(self):
        user = self.uf.validate(self.app.REQUEST, self.basic, [])
        self.assertEqual(user, None)

    def testNotValidateWithWrongRoles(self):
        user = self.uf.validate(self.app.REQUEST, self.basic, ['Manager'])
        self.assertEqual(user, None)

    def testAllowAccessToUser(self):
        self.login('user1')
        try:
            self.app.restrictedTraverse('doc')
        except Unauthorized:
            self.fail('Unauthorized')

    def testDenyAccessToAnonymous(self):
        self.assertRaises(Unauthorized, self.app.restrictedTraverse, 'doc')

    def testMaxListUsers(self):
        # create a folder-ish thing which contains a roleManager,
        # then put an acl_users object into the folde-ish thing

        class Folderish(BasicUserFolder):
            def __init__(self, size, count):
                self.maxlistusers = size
                self.users = []
                self.acl_users = self
                self.__allow_groups__ = self
                for i in xrange(count):
                    self.users.append("Nobody")

            def getUsers(self):
                return self.users

            def user_names(self):
                return self.getUsers()


        tinyFolderOver = Folderish(15, 20)
        tinyFolderUnder = Folderish(15, 10)

        assert tinyFolderOver.maxlistusers == 15
        assert tinyFolderUnder.maxlistusers == 15
        assert len(tinyFolderOver.user_names()) == 20
        assert len(tinyFolderUnder.user_names()) == 10

        try:
            list = tinyFolderOver.get_valid_userids()
            assert 0, "Did not raise overflow error"
        except OverflowError:
            pass

        try:
            list = tinyFolderUnder.get_valid_userids()
            pass
        except OverflowError:
            assert 0, "Raised overflow error erroneously"


class UserTests(unittest.TestCase):

    def testGetUserName(self):
        f = User('chris', '123', ['Manager'], [])
        self.assertEqual(f.getUserName(), 'chris')
        
    def testGetUserId(self):
        f = User('chris', '123', ['Manager'], [])
        self.assertEqual(f.getId(), 'chris')

    def testBaseUserGetIdEqualGetName(self):
        # this is true for the default user type, but will not
        # always be true for extended user types going forward (post-2.6)
        f = User('chris', '123', ['Manager'], [])
        self.assertEqual(f.getId(), f.getUserName())

    def testGetPassword(self):
        f = User('chris', '123', ['Manager'], [])
        self.assertEqual(f._getPassword(), '123')

    def testGetRoles(self):
        f = User('chris', '123', ['Manager'], [])
        self.assertEqual(f.getRoles(), ('Manager', 'Authenticated'))

    def testGetDomains(self):
        f = User('chris', '123', ['Manager'], [])
        self.assertEqual(f.getDomains(), ())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(UserFolderTests))
    suite.addTest(unittest.makeSuite(UserTests))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

