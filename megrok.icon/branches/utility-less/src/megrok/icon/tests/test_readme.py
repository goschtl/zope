import os.path
import unittest
from zope.testing import module
from zope.app.testing import functional
from grokcore.component.testing import grok_component


ftesting_zcml = os.path.join(os.path.dirname(__file__), 'ftesting.zcml')
FunctionalLayer = functional.ZCMLLayer(
    ftesting_zcml, __name__, 'FunctionalLayer', allow_teardown=True)


def setUp(test):
    module.setUp(test, 'megrok.icon.tests')


def test_suite():
    globs = {'grok_component': grok_component}
    suite = unittest.TestSuite()
    readme = functional.FunctionalDocFileSuite(
        '../README.txt', setUp=setUp, globs=globs)
    readme.layer = FunctionalLayer
    suite.addTest(readme)
    return suite
