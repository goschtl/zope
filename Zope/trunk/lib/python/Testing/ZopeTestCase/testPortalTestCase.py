#
# Tests the PortalTestCase
#
# NOTE: This is *not* an example TestCase. Do not
# use this file as a blueprint for your own tests!
#
# See testPythonScript.py and testShoppingCart.py for
# example test cases. See testSkeleton.py for a quick
# way of getting started.
#

# $Id: testPortalTestCase.py,v 1.24 2004/09/09 18:48:59 shh42 Exp $

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

from Acquisition import aq_base
from AccessControl import getSecurityManager
from types import ListType
from transaction import begin

portal_name = 'dummy_1_'
user_name = ZopeTestCase.user_name


def hasattr_(ob, attr):
    return hasattr(aq_base(ob), attr)


# Dummy Portal

from OFS.SimpleItem import SimpleItem
from OFS.Folder import Folder       

class DummyMembershipTool(SimpleItem):
    id = 'portal_membership'                
    def createMemberarea(self, member_id):      
        portal = self.aq_inner.aq_parent            
        portal.Members.manage_addFolder(member_id)          
    def getHomeFolder(self, member_id):                             
        portal = self.aq_inner.aq_parent
        return portal.Members[member_id]
                  
class DummyPortal(Folder):
    _v_skindata = None                
    def __init__(self, id):
        self.id = id
        self._addRole('Member') 
        self._setObject('portal_membership', DummyMembershipTool())
        self.manage_addFolder('Members')
    def setupCurrentSkin(self):
        if self._v_skindata is None:
            self._v_skindata = 'refreshed'


class TestPortalTestCase(ZopeTestCase.PortalTestCase):
    '''Incrementally exercise the PortalTestCase API.'''

    _setUp = ZopeTestCase.PortalTestCase.setUp
    _tearDown = ZopeTestCase.PortalTestCase.tearDown

    def getPortal(self):
        self.app._setObject(portal_name, DummyPortal(portal_name))
        return self.app[portal_name]

    def setUp(self):
        # For this test case we *want* to start
        # with an empty fixture.
        self._called = []
        # Implicitly aborts previous transaction
        begin()

    def beforeSetUp(self):
        self._called.append('beforeSetUp')

    def afterSetUp(self):
        self._called.append('afterSetUp')

    def beforeTearDown(self):
        self._called.append('beforeTearDown')

    def beforeClose(self):
        self._called.append('beforeClose')

    def afterClear(self):
        self._called.append('afterClear')

    def test_getPortal(self):
        # Portal should be set up
        self.app = self._app()
        self.portal = self.getPortal()
        self.failUnless(hasattr_(self.app, portal_name))
        self.failUnless(hasattr_(self.portal, 'Members'))
        self.failUnless(hasattr_(self.portal, 'portal_membership'))
        self.failUnless('Member' in self.portal.userdefined_roles())

    def test_setupUserFolder(self):
        # User folder should be set up.
        self.app = self._app()
        self.portal = self.getPortal()
        self.failIf(hasattr_(self.portal, 'acl_users'))
        self._setupUserFolder()
        self.failUnless(hasattr_(self.portal, 'acl_users'))
        # Must not complain if UF already exists
        self._setupUserFolder()

    def test_setupUser(self):
        # User should be set up
        self.app = self._app()
        self.portal = self.getPortal()
        self._setupUserFolder()
        self._setupUser()
        acl_user = self.portal.acl_users.getUserById(user_name)
        self.failUnless(acl_user)
        self.assertEqual(acl_user.getRoles(), ('Member', 'Authenticated'))
        self.assertEqual(type(acl_user.roles), ListType)

    def test_setupHomeFolder(self):
        # User's home folder should be set up
        self.app = self._app()
        self.portal = self.getPortal()
        self._setupUserFolder()
        self._setupUser()
        self.login()
        self._setupHomeFolder()
        self.failUnless(hasattr_(self.portal.Members, user_name))
        self.failIf(self.folder is None)
        # Shut up deprecation warnings
        try: owner_info = self.folder.getOwnerTuple()
        except AttributeError:
            owner_info = self.folder.getOwner(info=1)
        self.assertEqual(owner_info, ([portal_name, 'acl_users'], user_name))

    def test_refreshSkinData(self):
        # The _v_skindata attribute should be refreshed
        self.app = self._app()
        self.portal = self.getPortal()
        self.assertEqual(self.portal._v_skindata, None)
        self._refreshSkinData()
        self.assertEqual(self.portal._v_skindata, 'refreshed')

    def test_setRoles(self):
        # Roles should be set for user
        self.app = self._app()
        self.portal = self.getPortal()
        self._setupUserFolder()
        self._setupUser()
        test_roles = ['Manager', 'Member']
        self.setRoles(test_roles)
        acl_user = self.portal.acl_users.getUserById(user_name)
        self.assertRolesOfUser(test_roles, acl_user)

    def test_setRoles_2(self):
        # Roles should be set for logged in user
        self.app = self._app()
        self.portal = self.getPortal()
        self._setupUserFolder()
        self._setupUser()
        self.login()
        test_roles = ['Manager', 'Member']
        self.setRoles(test_roles)
        auth_user = getSecurityManager().getUser()
        self.assertRolesOfUser(test_roles, auth_user)

    def test_setRoles_3(self):
        # Roles should be set for a specified user
        self.app = self._app()
        self.portal = self.getPortal()
        self._setupUserFolder()
        self.portal.acl_users.userFolderAddUser('user_2', 'secret', [], [])
        test_roles = ['Manager', 'Member']
        self.setRoles(test_roles, 'user_2')
        acl_user = self.portal.acl_users.getUserById('user_2')
        self.assertRolesOfUser(test_roles, acl_user)

    def test_setRolesAssertsArgumentType(self):
        # setRoles should fail if 'roles' argument is not a list
        self.assertRaises(self.failureException, self.setRoles, 'foo')
        self.assertRaises(self.failureException, self.setRoles, ('foo',))

    def test_getRoles(self):
        # Should return roles of user
        self.app = self._app()
        self.portal = self.getPortal()
        self._setupUserFolder()
        self._setupUser()
        self.assertEqual(self.getRoles(), ('Member', 'Authenticated'))

    def test_getRoles_2(self):
        # Should return roles of specified user
        self.app = self._app()
        self.portal = self.getPortal()
        self._setupUserFolder()
        self.portal.acl_users.userFolderAddUser('user_2', 'secret', ['Manager'], [])
        self.assertEqual(self.getRoles('user_2'), ('Manager', 'Authenticated'))

    def test_setPermissions(self):
        # Permissions should be set for user
        self.app = self._app()
        self.portal = self.getPortal()
        test_perms = ['Add Folders']
        self.setPermissions(test_perms)
        self.assertPermissionsOfRole(test_perms, 'Member')

    def test_setPermissions_2(self):
        # Permissions should be set for specified role
        self.app = self._app()
        self.portal = self.getPortal()
        self.portal._addRole('role_2')
        test_perms = ['Add Folders']
        self.assertPermissionsOfRole([], 'role_2')
        self.setPermissions(test_perms, 'role_2')
        self.assertPermissionsOfRole(test_perms, 'role_2')

    def test_setPermissionsAssertsArgumentType(self):
        # setPermissions should fail if 'permissions' argument is not a list
        self.assertRaises(self.failureException, self.setPermissions, 'foo')
        self.assertRaises(self.failureException, self.setPermissions, ('foo',))

    def test_getPermissions(self):
        # Should return permissions of user
        self.app = self._app()
        self.portal = self.getPortal()
        test_perms = ['Add Folders']
        self.setPermissions(test_perms)
        self.assertEqual(self.getPermissions(), test_perms)

    def test_getPermissions_2(self):
        # Should return permissions of specified role
        self.app = self._app()
        self.portal = self.getPortal()
        test_perms = ['Add Folders']
        self.portal._addRole('role_2')
        self.setPermissions(test_perms, 'role_2')
        self.assertEqual(self.getPermissions('role_2'), test_perms)

    def test_login(self):
        # User should be able to log in
        self.app = self._app()
        self.portal = self.getPortal()
        self._setupUserFolder()
        self._setupUser()
        auth_name = getSecurityManager().getUser().getUserName()
        self.assertEqual(auth_name, 'Anonymous User')
        self.login()
        auth_name = getSecurityManager().getUser().getId()
        self.assertEqual(auth_name, user_name)

    def test_login_2(self):
        # A specified user should be logged in
        self.app = self._app()
        self.portal = self.getPortal()
        self._setupUserFolder()
        self.portal.acl_users.userFolderAddUser('user_2', 'secret', [], [])
        auth_name = getSecurityManager().getUser().getUserName()
        self.assertEqual(auth_name, 'Anonymous User')
        self.login('user_2')
        auth_name = getSecurityManager().getUser().getId()
        self.assertEqual(auth_name, 'user_2')

    def test_login_3(self):
        # Unknown user should raise AttributeError
        self.app = self._app()
        self.portal = self.getPortal()
        self._setupUserFolder()
        self.assertRaises(AttributeError, self.login, 'user_3')

    def test_logout(self):
        # User should be able to log out
        self.app = self._app()
        self.portal = self.getPortal()
        self._setupUserFolder()
        self._setupUser()
        self.login()
        self.logout()
        auth_name = getSecurityManager().getUser().getUserName()
        self.assertEqual(auth_name, 'Anonymous User')

    def test_clear(self):
        # Everything should be removed
        self.app = self._app()
        self.portal = self.getPortal()
        self._setupUserFolder()
        self._setupUser()
        self._setupHomeFolder()
        self._clear(1)
        self.failIf(self.app.__dict__.has_key(portal_name))
        auth_name = getSecurityManager().getUser().getUserName()
        self.assertEqual(auth_name, 'Anonymous User')
        self.assertEqual(self._called, ['beforeClose', 'afterClear'])
        # clear must not fail when called repeatedly
        self._clear()

    def test_setUp(self):
        # Everything should be set up
        self._setUp()
        self.failUnless(hasattr_(self.app, portal_name))
        self.failUnless(hasattr_(self.portal, 'acl_users'))
        self.failUnless(hasattr_(self.portal, 'Members'))
        self.failUnless(hasattr_(self.portal, 'portal_membership'))
        self.failUnless('Member' in self.portal.userdefined_roles())
        self.failUnless(hasattr_(self.portal.Members, user_name))
        acl_user = self.portal.acl_users.getUserById(user_name)
        self.failUnless(acl_user)
        self.assertEqual(acl_user.getRoles(), ('Member', 'Authenticated'))
        self.assertEqual(type(acl_user.roles), ListType)
        auth_name = getSecurityManager().getUser().getId()
        self.assertEqual(auth_name, user_name)
        # XXX: Changed in 0.9.0
        #self.assertEqual(self._called, ['afterClear', 'beforeSetUp', 'afterSetUp'])
        self.assertEqual(self._called, ['beforeSetUp', 'afterSetUp'])
        self.assertEqual(self.portal._v_skindata, 'refreshed')

    def test_tearDown(self):
        # Everything should be removed
        self._setUp()
        self._called = []
        self._tearDown()
        self.failIf(self.app.__dict__.has_key(portal_name))
        auth_name = getSecurityManager().getUser().getUserName()
        self.assertEqual(auth_name, 'Anonymous User')
        self.assertEqual(self._called, ['beforeTearDown', 'beforeClose', 'afterClear'])

    def test_configureFlag(self):
        # Nothing should be configured
        self._configure_portal = 0
        self._setUp()
        self.assertEqual(self.portal.acl_users.getUserById(user_name), None)
        self.failIf(hasattr_(self.portal.Members, user_name))
        auth_name = getSecurityManager().getUser().getUserName()
        self.assertEqual(auth_name, 'Anonymous User')
        # XXX: Changed in 0.9.0
        #self.assertEqual(self._called, ['afterClear', 'beforeSetUp', 'afterSetUp'])
        self.assertEqual(self._called, ['beforeSetUp', 'afterSetUp'])
        self.assertEqual(self.portal._v_skindata, 'refreshed')

    # This is crazy

    def __test_crazyRoles_0(self):
        # Permission assignments should be reset
        self.app = self._app()
        perms = self.getPermissionsOfRole('Anonymous', self.app)
        for perm in ['Access contents information', 'View', 'Query Vocabulary', 'Search ZCatalog']:
            if perm not in perms:
                self.fail('Expected permission "%s"' % perm)

    def __test_crazyRoles_1(self):
        # Permission assignments should be reset
        self.app = self._app()
        self.app.manage_role('Anonymous', ['View'])
        self.assertPermissionsOfRole(['View'], 'Anonymous', self.app)
        self.failIf(getSecurityManager().checkPermission('Access contents information', self.app))

    def __test_crazyRoles_2(self):
        # Permission assignments should be reset
        self.app = self._app()
        try:
            self.assertPermissionsOfRole(['View'], 'Anonymous', self.app)
        except self.failureException:
            pass

    def __test_crazyRoles_3(self):
        # Permission assignments should be reset
        self.app = self._app()
        self.failUnless(getSecurityManager().checkPermission('Access contents information', self.app))

    def __test_crazyRoles_4(self):
        # Permission assignments should be reset
        self.app = self._app()
        perms = self.getPermissionsOfRole('Anonymous', self.app)
        for perm in ['Access contents information', 'View', 'Query Vocabulary', 'Search ZCatalog']:
            if perm not in perms:
                self.fail('Expected permission "%s"' % perm)

    # Helpers

    def getPermissionsOfRole(self, role, context=None):
        '''Returns sorted list of permission names of the
           given role in the given context.
        '''
        if context is None:
            context = self.portal
        perms = context.permissionsOfRole(role)
        return [p['name'] for p in perms if p['selected']]

    def assertPermissionsOfRole(self, permissions, role, context=None):
        '''Compares list of permission names to permissions of the
           given role in the given context. Fails if the lists are not
           found equal.
        '''
        lhs = list(permissions)[:]
        lhs.sort()
        rhs = self.getPermissionsOfRole(role, context)
        rhs.sort()
        self.assertEqual(lhs, rhs)

    def assertRolesOfUser(self, roles, user):
        '''Compares list of role names to roles of user. Fails if the
           lists are not found equal.
        '''
        lhs = list(roles)[:]
        lhs.sort()
        rhs = list(user.getRoles())[:]
        rhs.remove('Authenticated')
        rhs.sort()
        self.assertEqual(lhs, rhs)


from AccessControl.User import UserFolder

class WrappingUserFolder(UserFolder):
    '''User folder returning wrapped user objects'''

    def getUser(self, name):
        return UserFolder.getUser(self, name).__of__(self)


class TestPlainUserFolder(ZopeTestCase.PortalTestCase):
    '''Tests whether user objects are properly wrapped'''

    def getPortal(self):
        self.app._setObject(portal_name, DummyPortal(portal_name))
        return self.app[portal_name]

    def testGetUserDoesNotWrapUser(self):
        user = self.portal.acl_users.getUserById(user_name)
        self.failIf(hasattr(user, 'aq_base'))
        self.failUnless(user is aq_base(user))

    def testLoggedInUserIsWrapped(self):
        user = getSecurityManager().getUser()
        self.assertEqual(user.getId(), user_name)
        self.failUnless(hasattr(user, 'aq_base'))
        self.failUnless(user.__class__.__name__, 'User')
        self.failUnless(user.aq_parent.__class__.__name__, 'UserFolder')
        self.failUnless(user.aq_parent.aq_parent.__class__.__name__, 'Folder')


class TestWrappingUserFolder(ZopeTestCase.PortalTestCase):
    '''Tests whether user objects are properly wrapped'''

    def getPortal(self):
        self.app._setObject(portal_name, DummyPortal(portal_name))
        return self.app[portal_name]

    def _setupUserFolder(self):
        self.portal._setObject('acl_users', WrappingUserFolder())

    def testGetUserWrapsUser(self):
        user = self.portal.acl_users.getUserById(user_name)
        self.failUnless(hasattr(user, 'aq_base'))
        self.failIf(user is aq_base(user))
        self.failUnless(user.aq_parent.__class__.__name__, 'WrappingUserFolder')

    def testLoggedInUserIsWrapped(self):
        user = getSecurityManager().getUser()
        self.assertEqual(user.getId(), user_name)
        self.failUnless(hasattr(user, 'aq_base'))
        self.failUnless(user.__class__.__name__, 'User')
        self.failUnless(user.aq_parent.__class__.__name__, 'WrappingUserFolder')
        self.failUnless(user.aq_parent.aq_parent.__class__.__name__, 'Folder')


# Because we override setUp we need to test again

class HookTest(ZopeTestCase.PortalTestCase):

    def setUp(self):
        self._called = []
        ZopeTestCase.PortalTestCase.setUp(self)
        
    def beforeSetUp(self):
        self._called.append('beforeSetUp')
        ZopeTestCase.PortalTestCase.beforeSetUp(self)
        
    def _setup(self):
        self._called.append('_setup')
        ZopeTestCase.PortalTestCase._setup(self)
        
    def afterClear(self):
        self._called.append('afterClear')
        ZopeTestCase.PortalTestCase.afterClear(self)
        
    def assertHooks(self, sequence):
        self.assertEqual(self._called, sequence)


class TestSetUpRaises(HookTest):

    def getPortal(self):
        self.app._setObject(portal_name, DummyPortal(portal_name))
        return self.app[portal_name]

    class Error: pass

    def setUp(self):
        try:
            HookTest.setUp(self)
        except self.Error:
            self.assertHooks(['beforeSetUp', '_setup', 'afterClear'])
            # Connection has been closed
            from Testing.ZopeTestCase import base
            self.assertEqual(len(base._connections), 0)
    
    def _setup(self):
        HookTest._setup(self)
        raise self.Error
    
    def testTrigger(self):
        pass


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortalTestCase))
    suite.addTest(makeSuite(TestPlainUserFolder))
    suite.addTest(makeSuite(TestWrappingUserFolder))
    suite.addTest(makeSuite(TestSetUpRaises))
    return suite

if __name__ == '__main__':
    framework()

