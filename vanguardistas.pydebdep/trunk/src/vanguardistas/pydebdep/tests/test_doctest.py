import unittest
import doctest

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite('vanguardistas.pydebdep.translator'))
    suite.addTest(doctest.DocTestSuite('vanguardistas.pydebdep.pydebdep'))
    return suite
