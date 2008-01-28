import unittest

from zope.testing import doctest
from zope.configuration.config import ConfigurationMachine

from martian import scan

optionflags = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS

def setUp(test):
    test.globs['config'] = ConfigurationMachine()

def test_suite():
    return doctest.DocFileSuite(
            'adapter.txt',
            setUp=setUp,
            optionflags=optionflags
            )


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

