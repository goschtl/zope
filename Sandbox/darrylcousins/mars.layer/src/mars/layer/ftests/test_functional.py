import os
import unittest

from zope.testing import doctest
from zope.app.testing import functional

minimal_zcml = os.path.join(os.path.dirname(__file__), 'minimal-ftesting.zcml')
TestMinimalLayer = functional.ZCMLLayer(
                       minimal_zcml, __name__, 'TestMinimalLayer')
pagelet_zcml = os.path.join(os.path.dirname(__file__), 'pagelet-ftesting.zcml')
TestPageletLayer = functional.ZCMLLayer(
                       pagelet_zcml, __name__, 'TestPageletLayer')

optionflags = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS

def setUp(test):
    functional.FunctionalTestSetup().setUp()

def tearDown(test):
    functional.FunctionalTestSetup().tearDown()

def test_suite():
    suite = unittest.TestSuite()
    dottedname = 'mars.layer.ftests.%s'
    for name in ['minimal', 'directive']:
        test = doctest.DocTestSuite(
                    dottedname % name, setUp=setUp,
                    tearDown=tearDown, optionflags=optionflags)
        test.layer = TestMinimalLayer
        suite.addTest(test)
    test = doctest.DocTestSuite(
                dottedname % 'pagelet', setUp=setUp,
                tearDown=tearDown, optionflags=optionflags)
    test.layer = TestPageletLayer
    suite.addTest(test)
    return suite



if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


