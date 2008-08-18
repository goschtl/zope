import unittest
import doctest
from zope.testing.doctestunit import DocTestSuite,DocFileSuite

from ocql.testing import utils

def test_suite():
    flags =  doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
    return unittest.TestSuite((
# avoid this tests for convenient while adding new implementation to the algebra optimizer
#need to add aoptimizer.txt
        DocFileSuite('aoptimizer.txt',
            optionflags=flags,
            setUp = utils.setupAdapters),
        DocFileSuite('aoptimizer_all.txt',
            optionflags=flags,
            setUp = utils.setupAdapters),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
