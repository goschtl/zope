import Zope
from unittest import TestCase,TestSuite,makeSuite,main
from Products.CMFCore.ActionsTool import ActionsTool
from Products.CMFCore.TypesTool import TypesTool
from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFDefault.URLTool import URLTool
from Products.CMFDefault.RegistrationTool import RegistrationTool
from Products.CMFDefault.MembershipTool import MembershipTool
import ZPublisher.HTTPRequest
from Testing.makerequest import makerequest

class ActionsToolTests( TestCase ):

    def setUp( self ):
        
        get_transaction().begin()
        self.connection = Zope.DB.open()
        root = self.connection.root()[ 'Application' ]
        root = self.root = makerequest(root)
        
        root._setObject( 'portal_actions', ActionsTool() )
        root._setObject('foo', URLTool() )
        self.tool = root.portal_actions
        self.ut = root.foo
        self.tool.action_providers = ('portal_actions',)

    def tearDown(self):
        get_transaction().abort()
        self.connection.close()
        
    def test_actionProviders(self):
        tool = self.tool
        self.assertEqual(tool.listActionProviders(), ('portal_actions',))

    def test_addActionProvider(self):
        tool = self.tool
        tool.addActionProvider('foo')
        self.assertEqual(tool.listActionProviders(),
                          ('portal_actions', 'foo'))

    def test_delActionProvider(self):
        tool = self.tool
        tool.deleteActionProvider('foo')
        self.assertEqual(tool.listActionProviders(),
                          ('portal_actions',))

    def test_listActionInformationActions(self):
        """
        Check that listFilteredActionsFor works for objects
        that return ActionInformation objects
        """
        root = self.root
        tool = self.tool
        root._setObject('portal_registration', RegistrationTool())
        root._setObject('portal_membership', MembershipTool())
        root._setObject('portal_types', TypesTool())
        self.tool.action_providers = ('portal_actions','portal_registration')
        tool.listFilteredActionsFor(root.portal_registration)
        
    def test_listDictionaryActions(self):
        """
        Check that listFilteredActionsFor works for objects
        that return dictionaries
        """
        root = self.root
        tool = self.tool
        root._setObject('donkey', PortalFolder('donkey'))
        root._setObject('portal_membership', MembershipTool())
        root._setObject('portal_types', TypesTool())
        print tool.listFilteredActionsFor(root.donkey)


def test_suite():
    return TestSuite((
        makeSuite(ActionsToolTests),
        ))

def run():
    main(defaultTest='test_suite')

if __name__ == '__main__':
    run()
