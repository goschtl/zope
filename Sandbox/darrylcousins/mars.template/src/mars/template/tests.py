import unittest
from zope.testing import doctest

optionflags = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS

def setUp(test):
    pass

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([doctest.DocFileSuite('./template.txt',
                             setUp=setUp,
                             optionflags=optionflags),
                   ])

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

