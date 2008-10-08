import unittest
from zope.app.testing import functional
from talk.z3cform import testing

def test_suite():
    suite = functional.FunctionalDocFileSuite('README.txt')
    suite.layer = testing.Z3CFormLayer
    return unittest.TestSuite((suite,))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
