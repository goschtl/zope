from unittest import TestCase, TestSuite, makeSuite, main

import Zope
try:
    from Interface.Verify import verifyClass
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import verify_class_implementation as verifyClass


class RegistrationToolTests(TestCase):

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

    def test_minPasswordLength(self):

        tool = self._makeOne()



def test_suite():
    return TestSuite((
        makeSuite( RegistrationToolTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
