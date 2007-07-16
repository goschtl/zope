import unittest
from zope.testing import doctest

optionflags = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([doctest.DocFileSuite('adapter.txt',
                             optionflags=optionflags),
                   ])

    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

