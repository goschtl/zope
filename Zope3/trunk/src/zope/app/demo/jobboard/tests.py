import unittest, doctest




def test_suite():
    
    return unittest.TestSuite((
        doctest.DocTestSuite('zopeproducts.demo.jobboard.job'),
        doctest.DocTestSuite('zopeproducts.demo.jobboard.browser'),
        ))

if __name__ == '__main__': unittest.main()
