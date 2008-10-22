##########################################################################
# zopyx.smartprintng.core 
#
# (C) Zope Corporation and Contributor
# Written by Andreas Jung for Haufe Mediengruppe, Freiburg, Germany
# and ZOPYX Ltd. & Co. KG, Tuebingen, Germany
##########################################################################


"""
Tests, tests, tests.........
"""

import os
import unittest

from zope.interface import Interface, implements

from zopyx.smartprintng.core import resources

broken_filename = 'no-such-file.ini'
configuration_filename = os.path.join(os.path.dirname(__file__), 
                                      'resources', 'sample.ini')

class ISample(Interface): 
    pass

class SampleContent(object):
    implements(ISample)


class ResourcesTests(unittest.TestCase):

    def setUp(self):
        resources.resources_registry.clear()

    def testNonExistingResourcesConfiguration(self):
        self.assertRaises(resources.ConfigurationError, 
                          resources.registerResource, 
                          ISample, 
                          broken_filename)

    def testCorrectResourcesConfiguration(self):
        resources.registerResource(ISample, configuration_filename)

    def testCanNotRegisterSameConfigurationTwice(self):
        resources.registerResource(ISample, configuration_filename)
        self.assertRaises(resources.ConfigurationError, 
                          resources.registerResource, 
                          ISample, 
                          configuration_filename)

    def testGetResourcesForWithNonMatchingInterfaces(self):
        resources.registerResource(ISample, configuration_filename)
        self.assertEqual(len(resources.getResourcesFor(None)), 0)

    def testGetResourcesForWithMatchingInterfaces(self):
        resources.registerResource(ISample, configuration_filename)
        context = SampleContent()
        self.assertEqual(ISample.providedBy(context), True)
        self.assertEqual(len(resources.getResourcesFor(context)), 1)

    def testGetResourcesForWithSubclassedInterfaces(self):
        resources.registerResource(ISample, configuration_filename)

        class ISample2(ISample): pass
        class SampleContent2(SampleContent):
            implements(ISample2)

        context = SampleContent2()
        self.assertEqual(ISample.providedBy(context), True)
        self.assertEqual(ISample2.providedBy(context), True)
        self.assertEqual(len(resources.getResourcesFor(context)), 1)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(ResourcesTests))
    return suite

