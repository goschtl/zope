import unittest
from zope.testing import doctest

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('duration.txt'),
        doctest.DocTestSuite('zc.i18n.date')
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
