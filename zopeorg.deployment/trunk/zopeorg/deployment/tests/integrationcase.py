"""Base class for integration tests, based on ZopeTestCase and PloneTestCase.

Note that importing this module has various side-effects: it registers a set of
products with Zope, and it sets up a sandbox Plone site with the appropriate
products installed.
"""

from Testing import ZopeTestCase
from Products.Five import zcml
# Import PloneTestCase - this registers more products with Zope as a side effect
from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite

ZopeTestCase.installProduct("PythonField")
ZopeTestCase.installProduct("TALESField")
ZopeTestCase.installProduct("TemplateFields")
ZopeTestCase.installProduct("PloneFormGen")

# Set up a Plone site, and apply our custom extension profile
PROFILES = ('zopeorg.deployment:default',)
setupPloneSite(extension_profiles=PROFILES)

import zopeorg.deployment

class ZopeOrgLayer(PloneSite):
    @classmethod
    def setUp(cls):
        zcml.load_config('configure.zcml', zopeorg.deployment)
        ZopeTestCase.installPackage("zopeorg.deployment")

    @classmethod
    def tearDown(cls):
        pass


class IntegrationTestCase(PloneTestCase):
    """Base class for integration tests for the '${package}' product.

    This may provide specific set-up and tear-down operations, or provide
    convenience methods.
    """

    layer = ZopeOrgLayer

    def createMemberarea(self, name):
        # bypass PTC's creation of a home folder for the default user
        pass

