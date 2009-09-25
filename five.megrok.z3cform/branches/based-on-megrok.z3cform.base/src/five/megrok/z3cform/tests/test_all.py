import unittest
from pkg_resources import resource_listdir

from zope.testing import doctest
from zope.component import testing

import Products.Five
from Products.Five import zcml
import five.megrok.z3cform
import os


def setUp(test=None):
    testing.setUp(test)
    zcml.load_config('meta.zcml', package=Products.Five)
    zcml.load_config('configure.zcml', package=Products.Five)
    zcml.load_config('testing.zcml', package=five.megrok.z3cform)

from five.grok.testing import grok
from zope import component

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

        dottedname = 'five.megrok.z3cform.tests.%s.%s' % (name, filename[:-3])
        test = doctest.DocTestSuite(dottedname,
                                    setUp=setUp,
                                    tearDown=testing.tearDown,
                                    optionflags=doctest.ELLIPSIS+
                                                doctest.NORMALIZE_WHITESPACE)

        suite.addTest(test)
    return suite


def test_suite():
    suite = unittest.TestSuite()
    for name in ['form',]:
        suite.addTest(suiteFromPackage(name))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
