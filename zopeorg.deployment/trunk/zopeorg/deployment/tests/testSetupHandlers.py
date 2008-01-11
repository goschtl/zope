from zope.component import getUtility
from zope.component import getMultiAdapter
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
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

    def testPloneFormGenInstalled(self):
        qi=self.portal.portal_quickinstaller
        self.assertEqual(qi.isProductInstalled("PloneFormGen"), True)

    def testRightPortlets(self):
        rightColumn=getUtility(IPortletManager, name=u"plone.rightcolumn",
                                context=self.portal)
        right=getMultiAdapter((self.portal, rightColumn,),
                                IPortletAssignmentMapping, context=self.portal)
        self.assertEqual(right.keys(), [u"review"])



class TestContentHandler(IntegrationTestCase):
    def testNewContentIndexed(self):
        ct=self.portal.portal_catalog
        brains=ct(id="learn")
        self.assertEqual(len(brains), 1)
        brain=brains[0]
        self.assertEqual(brain.Title, "Learn")

def test_suite():
    from unittest import TestSuite, makeSuite
    suite=TestSuite()
    suite.addTest(makeSuite(TestDefaultHandler))
    suite.addTest(makeSuite(TestContentHandler))
    return suite

