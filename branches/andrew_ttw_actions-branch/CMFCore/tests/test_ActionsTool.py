import Zope
import unittest
import OFS.Folder, OFS.SimpleItem
import Acquisition
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl import SecurityManager
from Products.CMFCore.ActionsTool import *
from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.Expression import Expression
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.CMFCorePermissions import AddPortalContent, ManagePortal
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

class OmnipotentUser( Acquisition.Implicit ):
    """
        Stubbed out manager for unit testing purposes.
    """
    def getId( self ):
        return 'all_powerful_Oz'
    
    getUserName = getId

    def allowed( self, object, object_roles=None ):
        return 1

class UserWithRoles( Acquisition.Implicit ):
    """
        Stubbed out manager for unit testing purposes.
    """
    def __init__( self, *roles ):
        self._roles = roles

    def getId( self ):
        return 'high_roller'
    
    getUserName = getId

    def allowed( self, object, object_roles=None ):
        for orole in object_roles:
            if orole in self._roles:
                return 1
        return 0

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
        tool = root.portal_actions
        tool.action_providers = ('portal_actions')
        self.assertEqual(tool.listActionProviders(), ('portal_actions',))

    def tearDown( self ):
        get_transaction().abort()
        self.connection.close()
        noSecurityManager()
        SecurityManager.setSecurityPolicy(self._oldPolicy)

class ActionInformationTests(unittest.TestCase):
    
    def test_basic_construction(self):
        ai = ActionInformation(id='view'
                              )
        self.assertEqual(ai.getId(), 'view')
        self.assertEqual(ai.Title(), 'view')
        self.assertEqual(ai.Description(), '')
        self.assertEqual(ai.getCondition(), '')
        self.assertEqual(ai.getActionExpression(), '')
        self.assertEqual(ai.getPermissions(), ())

    def test_construction_with_Expressions(self):
        ai = ActionInformation(id='view'
                             , title='View'
                             , action=Expression(
             text='view')
                             , condition=Expression(
             text='member'))
        self.assertEqual(ai.getId(), 'view')
        self.assertEqual(ai.Title(), 'View')
        self.assertEqual(ai.Description(), '')
        self.assertEqual(ai.getCondition(), 'member')
        self.assertEqual(ai.getActionExpression(), 'view')
        self.assertEqual(ai.getPermissions(), ())
        

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ActionsToolTests))
    suite.addTest(unittest.makeSuite(ActionInformationTests))
    return suite

def run():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    run()
