import unittest
import doctest
from zope.testing.doctestunit import DocTestSuite,DocFileSuite

def test_suite():
    flags =  doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
    return unittest.TestSuite((
        DocFileSuite('queryobject_checks.txt',
            optionflags=flags),
        DocFileSuite('queryobject.txt',
            optionflags=flags),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
