from zope.testing import doctest
import unittest

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

import zope.component
import zope.component.testing
import zope.component.tests

from zope.configuration import xmlconfig

import z3c.discriminator

"""
Note:

To make sure the new adapter directive is correctly implemented,
we run the corresponding test suite from zope.component against
our implementation.
"""

def clearZCML(test=None):
    zope.component.testing.tearDown()
    zope.component.testing.setUp()

    xmlconfig.XMLConfig('meta.zcml', zope.component)()
    xmlconfig.XMLConfig('meta.zcml', z3c.discriminator)()

clearZCML_save = zope.component.tests.clearZCML

def setUp(test):
    zope.component.testing.setUp()
    zope.component.tests.clearZCML = clearZCML
    
def tearDown(test):
    zope.component.testing.tearDown()
    zope.component.tests.clearZCML = clearZCML_save
    
def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
                             optionflags=OPTIONFLAGS,
                             setUp=zope.component.testing.setUp,
                             tearDown=zope.component.testing.tearDown,
                             package="z3c.discriminator"),
        doctest.DocFileSuite('zcml.txt',
                             optionflags=OPTIONFLAGS,
                             setUp=setUp,
                             tearDown=tearDown,
                             package="zope.component"),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
