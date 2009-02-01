import unittest
from zope.testing import doctest

from zopesandbox.document import testing

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
                             setUp=testing.setUp,
                             tearDown=testing.tearDown),
    ))
