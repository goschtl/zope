import unittest

from Products.CMFCore.utils import getToolByName

from gzo.plonepolicy.tests.base import GzoPolicyTestCase

class TestSetup(GzoPolicyTestCase):

    def test_portal_title(self):
        self.assertEquals("Grok", self.portal.getProperty('title'))
    
    def test_theme_installed(self):
        skins = getToolByName(self.portal, 'portal_skins')
        layer = skins.getSkinPath('Grok Smash Theme')
        self.failUnless('smash_custom_templates' in layer)
        self.assertEquals('Grok Smash Theme', skins.getDefaultSkin())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite
