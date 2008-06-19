import unittest
import doctest
from zope.testing.doctestunit import DocTestSuite,DocFileSuite

def test_suite():
    flags =  doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
    return unittest.TestSuite((
        DocTestSuite('ocql.database.index')
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
