import unittest
from zope.testing import doctest, module
from zope.app.testing import functional
from megrok.resource.ftests import FunctionalLayer

def setUp(test):
    module.setUp(test, 'megrok.resource.ftests')

def tearDown(test):
    module.tearDown(test)

def test_suite():
    readme = functional.FunctionalDocFileSuite(
        '../README.txt', setUp=setUp, tearDown=tearDown,
        optionflags=(doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE),
        )
    readme.layer = FunctionalLayer
    suite = unittest.TestSuite()
    suite.addTest(readme)
    return suite

