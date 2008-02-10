import unittest
from zope.testing import doctest

from tfws.website import testing

optionflags = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([doctest.DocFileSuite('site.txt',
                       setUp=testing.setUp, tearDown=testing.tearDown,
                       optionflags=optionflags),
                   ])

    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

