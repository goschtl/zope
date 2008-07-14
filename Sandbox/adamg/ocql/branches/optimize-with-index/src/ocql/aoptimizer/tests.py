import unittest
import doctest
from zope.testing.doctestunit import DocTestSuite,DocFileSuite

def test_suite():
    flags =  doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
    return unittest.TestSuite((
# avoid this tests for convenient while adding new implementation to the algebra optimizer
#        DocFileSuite('aoptimizer.txt',
#            optionflags=flags),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
