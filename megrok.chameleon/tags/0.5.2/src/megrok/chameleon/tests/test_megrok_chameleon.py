"""Test setup for megrok.chameleon.
"""
import doctest
import unittest
import megrok.chameleon
from megrok.chameleon.tests import FunctionalLayer

FLAGS = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)

def test_suite():
    """Get a testsuite of all doctests.
    """
    suite = unittest.TestSuite()
    for name in ['README.txt']:
        test = doctest.DocFileSuite(
            name,
            package=megrok.chameleon,
            globs=dict(
                getRootFolder=FunctionalLayer.getRootFolder,
                ),
            optionflags=FLAGS,
            )
        test.layer = FunctionalLayer
        suite.addTest(test)
    return suite
