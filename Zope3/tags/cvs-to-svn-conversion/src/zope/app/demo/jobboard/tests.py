import unittest, doctest


def test_suite():
    
    return unittest.TestSuite((
        doctest.DocTestSuite('zope.app.demo.jobboard.job'),
        doctest.DocTestSuite('zope.app.demo.jobboard.browser'),
        ))

if __name__ == '__main__': unittest.main()
