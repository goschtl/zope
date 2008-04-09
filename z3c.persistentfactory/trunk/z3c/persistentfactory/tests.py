import unittest
from zope.testing import doctest

def test_suite():
    return doctest.DocFileSuite(
        'README.txt',
        'declarations.txt',
        'factory.txt',
        optionflags=(
            doctest.REPORT_NDIFF|
            doctest.NORMALIZE_WHITESPACE|
            doctest.ELLIPSIS))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
