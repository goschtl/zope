import unittest, doctest

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite('zope.app.browser.services.interface'),
        ))

if __name__ == '__main__':
    unittest.main()
