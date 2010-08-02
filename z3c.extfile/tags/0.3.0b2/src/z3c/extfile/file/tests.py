import doctest
import unittest
from zope.testing.doctestunit import DocFileSuite

def test_suite():

    return unittest.TestSuite(
        (
        DocFileSuite('file.txt',
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

