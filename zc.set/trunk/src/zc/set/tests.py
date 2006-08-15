import unittest

from zope.testing import doctest, module
import zc.set

def setUpSetsOne(test):
    test.globs['factory'] = set

def setUpSetsTwo(test):
    test.globs['factory'] = zc.set.Set

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt', setUp=setUpSetsOne),
        doctest.DocFileSuite('README.txt', setUp=setUpSetsTwo),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
