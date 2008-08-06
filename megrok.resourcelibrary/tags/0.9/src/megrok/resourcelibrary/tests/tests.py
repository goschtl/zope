import os
import unittest, doctest
from zope.app.testing import functional
from zope.testing import module, cleanup

ResourceLibraryFunctionalLayer = functional.ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'ResourceLibraryFunctionalLayer')
    
def setUp(test):
    module.setUp(test, 'megrok.resourcelibrary.tests')

def tearDown(test):
    module.tearDown(test)
    cleanup.cleanUp()

def test_suite():
    suite = functional.FunctionalDocFileSuite(
        '../README.txt',
        optionflags=doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS,
        setUp=setUp,
        tearDown=tearDown,
        )
    suite.layer = ResourceLibraryFunctionalLayer
    return unittest.TestSuite([
        suite,
        ])
