import unittest
import doctest

from zope import interface
from zope import schema
from zope import component

from zope.app.testing import setup
from zope.testing.doctestunit import DocFileSuite

import transaction

import testing

def setUp(test):
    setup.placefulSetUp()
    testing.setUp(test)
    
def tearDown(test):
    setup.placefulTearDown()
    testing.tearDown(test)
    
def test_suite():
    globs = dict(
        interface=interface,
        component=component,
        schema=schema)
    
    return unittest.TestSuite((
        DocFileSuite('README.txt',
                     setUp=setUp, tearDown=tearDown,
                     globs=globs,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
