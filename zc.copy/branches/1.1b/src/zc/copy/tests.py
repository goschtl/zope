import unittest
import zope.testing.module
from zope.testing import doctest
from zope.component import testing, eventtesting
from zope.app.container.tests.placelesssetup import PlacelessSetup

container_setup = PlacelessSetup()

def copierSetUp(test):
    zope.testing.module.setUp(test, 'zc.copy.doctest')
    testing.setUp(test)
    eventtesting.setUp(test)
    container_setup.setUp()

def copierTearDown(test):
    zope.testing.module.tearDown(test)
    testing.tearDown(test)

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.txt',
            setUp=copierSetUp,
            tearDown=copierTearDown),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
