import unittest
import zope.testing.doctest

import testing

def test_suite():
    return unittest.TestSuite((
        zope.testing.doctest.DocFileSuite(
            'jsevent.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=zope.testing.doctest.NORMALIZE_WHITESPACE |
                        zope.testing.doctest.ELLIPSIS),
        zope.testing.doctest.DocFileSuite(
            'jsvalidator.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=zope.testing.doctest.NORMALIZE_WHITESPACE |
                        zope.testing.doctest.ELLIPSIS),
        zope.testing.doctest.DocFileSuite(
            'jsbutton.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=zope.testing.doctest.NORMALIZE_WHITESPACE |
                        zope.testing.doctest.ELLIPSIS),
        ))
