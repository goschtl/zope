import unittest
import doctest
from zope.testing.doctestunit import DocTestSuite,DocFileSuite

from ocql.testing import utils

def test_suite():
    flags =  doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
    return unittest.TestSuite((
        DocFileSuite('compiler.txt',
            optionflags=flags,
            setUp = utils.setupAdapters),
        DocFileSuite('compiler_optimized.txt',
            optionflags=flags,
            setUp = utils.setupAdapters),
        DocFileSuite('compiler_optimized_testdata.txt',
            optionflags=flags,
            setUp = utils.setupAdapters),
        DocFileSuite('debug.txt',
            optionflags=flags,
            setUp = utils.setupAdapters),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
