import unittest

from zope.testing import doctestunit
from zope.component import testing

from Testing import ZopeTestCase

import Products.Five
from Products.Five import zcml

import five.grok

def setUp(test=None):
    testing.setUp(test)
    zcml.load_config('meta.zcml', package=Products.Five)
    zcml.load_config('configure.zcml', package=Products.Five)
    zcml.load_config('meta.zcml', package=five.grok)
    zcml.load_config('configure.zcml', package=five.grok)
    zcml.load_config('configure.zcml', package=five.grok.tests)

def test_suite():
    return unittest.TestSuite([

        # Unit tests for your API
        #doctestunit.DocFileSuite(
            #'README.txt', package='something.foo',
            #setUp=testing.setUp, tearDown=testing.tearDown),

        doctestunit.DocTestSuite(
            module='five.grok.tests.adapters',
            setUp=setUp, tearDown=testing.tearDown),

        doctestunit.DocTestSuite(
            module='five.grok.tests.utilities',
            setUp=setUp, tearDown=testing.tearDown),

        doctestunit.DocTestSuite(
            module='five.grok.tests.subscribers',
            setUp=setUp, tearDown=testing.tearDown),

        doctestunit.DocTestSuite(
            module='five.grok.tests.views',
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
