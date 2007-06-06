import unittest
import zope.testing.doctest

import testing

def test_suite():
    return unittest.TestSuite((
        zope.testing.doctest.DocFileSuite(
            'README.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=zope.testing.doctest.NORMALIZE_WHITESPACE |
                        zope.testing.doctest.ELLIPSIS),
        ))
