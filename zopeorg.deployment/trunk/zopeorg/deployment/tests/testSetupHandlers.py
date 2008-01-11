from zopeorg.deployment.tests.integrationcase import IntegrationTestCase

class TestDefaultHandler(IntegrationTestCase):
    """Test actions performed by the setup handler code.
    """
    def testMemberAreaDisabled(self):
        mt=self.portal.portal_membership
        self.assertEqual(mt.memberareaCreationFlag, 0)

    def testThemeInstalled(self):
        qi=self.portal.portal_quickinstaller
        self.assertEqual(qi.isProductInstalled("zopeorg.theme"), True)
        st=self.portal.portal_skins
        self.assertEqual(st.getDefaultSkin(), "Zope.org Theme")

def test_suite():
    from unittest import TestSuite, makeSuite
    suite=TestSuite()
    suite.addTest(makeSuite(TestDefaultHandler))
    return suite

