import unittest
from zope.app.testing import functional

try:
    from z3c import sampledata
    sampledata = True
except ImportError:
    sampledata = False

functional.defineLayer('TestLayer', 'ftesting.zcml')


def setUp(test):
    """Setup a reasonable environment for the tag tests"""
    pass


def tearDown(test):
    pass


def test_suite():
    suite = unittest.TestSuite()
    if not sampledata:
        return suite
    suites = (
        functional.FunctionalDocFileSuite('browser/README.txt',
                                          setUp=setUp, tearDown=tearDown,
                                          ),
        )
    for s in suites:
        s.layer=TestLayer
        suite.addTest(s)
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
