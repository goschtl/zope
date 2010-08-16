import doctest
import unittest

def test_suite():
    return unittest.TestSuite(
        (
        doctest.DocFileSuite(
                'README.txt',
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                ),
        doctest.DocFileSuite(
                'magic.txt',
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                ),
        doctest.DocTestSuite(
                'z3c.filetype.api',
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                ),
            ))
