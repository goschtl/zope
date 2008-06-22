"""
Do a functional test on the app.

:Test-Layer: python
"""
from flint.app import Flint
from flint.testing import FunctionalLayer
from zope.app.testing.functional import FunctionalTestCase
class FlintFunctionalTest(FunctionalTestCase):
    layer = FunctionalLayer
class SimpleFlintFunctionalTest(FlintFunctionalTest):
    """ This the app in ZODB. """
    def test_simple(self):
        """ test creating a Flint instance into Zope """
        root = self.getRootFolder()
        root['instance'] = Flint()
        self.assertEqual(root.get('instance').__class__, Flint)
