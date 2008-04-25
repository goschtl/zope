import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase
from Products.Five import zcml
import five.grokkers

def setUp(test=None):
    testing.setUp(test)
    zcml.load_config('meta.zcml', package=five.grokkers)
    zcml.load_config('configure.zcml', package=five.grokkers.tests)

def test_suite():
    return unittest.TestSuite([

        # Unit tests for your API
        #doctestunit.DocFileSuite(
            #'README.txt', package='something.foo',
            #setUp=testing.setUp, tearDown=testing.tearDown),

        doctestunit.DocTestSuite(
            module='five.grokkers.tests.adapters',
            setUp=setUp, tearDown=testing.tearDown),

        # Integration tests that use ZopeTestCase
        #ztc.ZopeDocFileSuite(
        #    'README.txt', package='something.foo',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        #ztc.FunctionalDocFileSuite(
        #    'browser.txt', package='something.foo'),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
