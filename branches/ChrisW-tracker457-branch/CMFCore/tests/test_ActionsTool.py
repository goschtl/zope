import Zope
from unittest import TestCase,TestSuite,makeSuite,main
from Products.CMFCore.ActionsTool import *
from Products.CMFDefault.URLTool import *
import ZPublisher.HTTPRequest
from Testing.makerequest import makerequest

class ActionsToolTests( TestCase ):

    def setUp( self ):
        
        root = self.root = makerequest(Zope.app())
        root._setObject( 'portal_actions', ActionsTool() )
        root._setObject('foo', URLTool() )
        self.tool = root.portal_actions
        self.ut = root.foo
        self.tool.action_providers = ('portal_actions',)

    def tearDown(self):
        get_transaction().abort()
        
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

def test_suite():
    return TestSuite((
        makeSuite(ActionsToolTests),
        ))

def run():
    main(defaultTest='test_suite')

if __name__ == '__main__':
    run()
