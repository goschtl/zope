#
# Abstract base test case for working with CMF-style portals
#
# This base class maintains a fixture consisting of:
#
#   - a portal object (self.portal)
#   - a user folder inside the portal
#   - a default user with role 'Member' inside the user folder
#   - the default user's memberarea (self.folder)
#   - the default user is logged in
#
# The twist is that the portal object itself is *not* created
# by the PortalTestCase class! Subclasses must make sure
# getPortal() returns a usable portal object to the setup code.
#

# $Id: PortalTestCase.py,v 1.38 2005/02/09 12:42:40 shh42 Exp $

import base
import interfaces
import utils

from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from Acquisition import aq_base

portal_name = 'portal'
from ZopeTestCase import user_name
from ZopeTestCase import user_password


class PortalTestCase(base.TestCase):
    '''Base test case for testing CMF-style portals'''

    __implements__ = (interfaces.IPortalTestCase,
                      interfaces.IPortalSecurity,
                      base.TestCase.__implements__)

    _configure_portal = 1

    def setUp(self):
        '''Sets up the fixture. Do not override,
           use the hooks instead.
        '''
        try:
            self.beforeSetUp()
            self.app = self._app()
            self.portal = self._portal()
            self._setup()
            self._refreshSkinData()
            self.afterSetUp()
        except:
            self._clear()
            raise

    def _portal(self):
        '''Returns the portal object for a test.'''
        return self.getPortal()

    def _setup(self):
        '''Configures the portal. Framework authors may
           override.
        '''
        if self._configure_portal:
            self._setupUserFolder()
            self._setupUser()
            self.login()
            self._setupHomeFolder()

    def _setupUserFolder(self):
        '''Creates the user folder if missing.'''
        if not hasattr(aq_base(self.portal), 'acl_users'):
            self.portal.manage_addUserFolder()

    def _setupUser(self):
        '''Creates the default user.'''
        uf = self.portal.acl_users
        uf.userFolderAddUser(user_name, user_password, ['Member'], [])

    def _setupHomeFolder(self):
        '''Creates the default user's home folder.'''
        self.createMemberarea(user_name)
        pm = self.portal.portal_membership
        self.folder = pm.getHomeFolder(user_name)

    def _refreshSkinData(self):
        '''Refreshes the magic _v_skindata attribute.'''
        if hasattr(self.portal, '_v_skindata'):
            self.portal._v_skindata = None
        if hasattr(self.portal, 'setupCurrentSkin'):
            self.portal.setupCurrentSkin()

    # Portal interface

    def getPortal(self):
        '''Returns the portal object to the setup code.
           Will typically be overridden by subclasses
           to return the object serving as the "portal".

           Note: This method should not be called by tests!
        '''
        return self.app[portal_name]

    def createMemberarea(self, name):
        '''Creates a memberarea for the specified user.
           Subclasses may override to provide a customized
           or more lightweight version of the memberarea.
        '''
        pm = self.portal.portal_membership
        pm.createMemberarea(name)

    # Security interface

    def setRoles(self, roles, name=user_name):
        '''Changes the user's roles.'''
        uf = self.portal.acl_users
        uf.userFolderEditUser(name, None, utils.makelist(roles), [])
        if name == getSecurityManager().getUser().getId():
            self.login(name)

    def setPermissions(self, permissions, role='Member'):
        '''Changes the permissions assigned to role.'''
        self.portal.manage_role(role, utils.makelist(permissions))

    def login(self, name=user_name):
        '''Logs in.'''
        uf = self.portal.acl_users
        user = uf.getUserById(name)
        if not hasattr(user, 'aq_base'):
            user = user.__of__(uf)
        newSecurityManager(None, user)

    def logout(self):
        '''Logs out.'''
        noSecurityManager()

    # b/w compatibility methods

    def _setRoles(self, roles, name=user_name):
        self.setRoles(roles, name)
    def _setPermissions(self, permissions, role='Member'):
        self.setPermissions(permissions, role)
    def _login(self, name=user_name):
        self.login(name)
    def _logout(self):
        self.logout()


# b/w compatibility names
_portal_name = portal_name

