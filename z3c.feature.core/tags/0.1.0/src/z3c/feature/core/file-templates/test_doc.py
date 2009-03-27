import unittest
import zope.testing.doctest

def test_suite():
    return unittest.TestSuite((

        zope.testing.doctest.DocFileSuite(
            '../README.txt',
            optionflags=zope.testing.doctest.NORMALIZE_WHITESPACE |
                        zope.testing.doctest.ELLIPSIS),


        ))
