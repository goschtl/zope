import doctest
import unittest
from zope.testing.doctestunit import DocFileSuite, DocTestSuite

def test_suite():
    
    return unittest.TestSuite(
        (
        DocFileSuite('README.txt',
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('magic.txt',
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocTestSuite('z3c.filetype.api',
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

