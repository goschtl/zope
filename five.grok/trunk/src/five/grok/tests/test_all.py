import unittest
from pkg_resources import resource_listdir

from zope.testing import doctestunit, doctest
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

    
def suiteFromPackage(name):
    files = resource_listdir(__name__, name)
    suite = unittest.TestSuite()
    for filename in files:
        if not filename.endswith('.py'):
            continue
        if filename.endswith('_fixture.py'):
            continue
        if filename == '__init__.py':
            continue

        dottedname = 'five.grok.tests.%s.%s' % (name, filename[:-3])
        test = doctest.DocTestSuite(dottedname,
                                    setUp=setUp,
                                    tearDown=testing.tearDown, 
                                    optionflags=doctest.ELLIPSIS+
                                                doctest.NORMALIZE_WHITESPACE)

        suite.addTest(test)
    return suite
    
def test_suite():
    return unittest.TestSuite([

        doctestunit.DocTestSuite(
            module='five.grok.tests.adapters',
            setUp=setUp, tearDown=testing.tearDown),

        doctestunit.DocTestSuite(
            module='five.grok.tests.multiadapter',
            setUp=setUp, tearDown=testing.tearDown),

        doctestunit.DocTestSuite(
            module='five.grok.tests.utilities',
            setUp=setUp, tearDown=testing.tearDown),

        doctestunit.DocTestSuite(
            module='five.grok.tests.subscribers',
            setUp=setUp, tearDown=testing.tearDown),
        
        ])
        
        
if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
