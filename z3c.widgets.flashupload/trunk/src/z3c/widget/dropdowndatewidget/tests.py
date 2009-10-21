import unittest

from zope.testing import doctest
from zope.testing.doctestunit import DocFileSuite


def test_suite():
    return unittest.TestSuite((
        DocFileSuite('README.txt',
             optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
             ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
