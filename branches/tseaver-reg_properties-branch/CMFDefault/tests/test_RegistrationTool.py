from unittest import TestCase, TestSuite, makeSuite, main

import Zope

try:
    from Interface.Verify import verifyClass
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import verify_class_implementation as verifyClass

from Products.CMFCore.tests.base.testcase import TransactionalTest

class DummyMembershipTool:

    def getMemberById( self, id ):

        return None

class RegistrationToolTests(TransactionalTest):

    def _getTargetClass(self):
        from Products.CMFDefault.RegistrationTool import RegistrationTool
        return RegistrationTool

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw )

    def test_interface(self):

        from Products.CMFCore.interfaces.portal_registration \
                import portal_registration as IRegistrationTool
        from Products.CMFCore.interfaces.portal_actions \
                import ActionProvider as IActionProvider

        verifyClass(IRegistrationTool, self._getTargetClass())
        verifyClass(IActionProvider, self._getTargetClass())

    def test_testPasswordValidity_min_password_length(self):

        tool = self._makeOne()

        error = tool.testPasswordValidity( 'abc', 'abc' )
        self.failIf( error is None )

        tool.min_password_length = 3
        error = tool.testPasswordValidity( 'abc', 'abc' )
        self.failUnless( error is None )

    def test_testPropertiesValidity(self):

        tool = self._makeOne().__of__( self.root )
        self.root.portal_membership = DummyMembershipTool()

        error = tool.testPropertiesValidity( { 'username' : '_abc' 
                                             } )

        self.failIf( error is None )

        error = tool.testPropertiesValidity( { 'username' : 'abc' 
                                             } )

        self.failIf( error is None )

        error = tool.testPropertiesValidity( { 'username' : 'abc' 
                                             , 'email' : 'foo@example.com'
                                             } )

        self.failUnless( error is None, error )


def test_suite():
    return TestSuite((
        makeSuite( RegistrationToolTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
