import Zope
import unittest
import OFS.Folder, OFS.SimpleItem
import Acquisition
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl import SecurityManager
from Products.CMFCore.ActionsTool import *
from Products.CMFCore.CMFCorePermissions import AddPortalContent
from Products.CMFCore.CMFCorePermissions import ModifyPortalContent
from Products.CMFCore import utils
import ZPublisher.HTTPRequest

class PermissiveSecurityPolicy:
    """
        Stub out the existing security policy for unit testing purposes.
    """
    #
    #   Standard SecurityPolicy interface
    #
    def validate( self
                , accessed=None
                , container=None
                , name=None
                , value=None
                , context=None
                , roles=None
                , *args
                , **kw):
        return 1
    
    def checkPermission( self, permission, object, context) :
        if permission == 'forbidden permission':
            return 0
        return 1

class UnitTestUser( Acquisition.Implicit ):
    """
        Stubbed out manager for unit testing purposes.
    """
    def getId( self ):
        return 'unit_tester'
    
    getUserName = getId

    def allowed( self, object, object_roles=None ):
        # for testing permissions on actions
        if object.getId() == 'actions_dummy':
            if 'Anonymous' in object_roles:
                return 1
            else:
                return 0
        return 1

class ActionsToolTests( unittest.TestCase ):

    def setUp( self ):
        get_transaction().begin()
        self._policy = PermissiveSecurityPolicy()
        self._oldPolicy = SecurityManager.setSecurityPolicy(self._policy)
        self.connection = Zope.DB.open()
        root = self.root = self.connection.root()[ 'Application' ]
        newSecurityManager( None, UnitTestUser().__of__( self.root ) )

        env = { 'SERVER_NAME' : 'http://localhost'
              , 'SERVER_PORT' : '80'
              }
        root.REQUEST = ZPublisher.HTTPRequest.HTTPRequest( None, env, None )
        
        root._setObject( 'portal_actions', ActionsTool() )
        self.tool = tool = root.portal_actions
        tool.action_providers = ('portal_actions',)

    def test_actionProviders(self):
        tool = self.tool
        self.assertEqual(tool.listActionProviders(), ('portal_actions',))

    def tearDown( self ):
        get_transaction().abort()
        self.connection.close()
        noSecurityManager()
        SecurityManager.setSecurityPolicy(self._oldPolicy)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ActionsToolTests))
    return suite

def run():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    run()
