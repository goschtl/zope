import unittest
from pkg_resources import resource_listdir

from grok.ftests.test_grok_functional import FunctionalDocTestSuite

from zope.app.testing import functional

from martian.tests.test_all import globs, optionflags

functional.defineLayer('TestLayer', 'ftesting.zcml')
functional.defineLayer('TestMinimalLayer', 'minimal-ftesting.zcml')

def test_suite():
    suite = unittest.TestSuite()
    dottedname = 'mars.template.tests.%s'

    for name in ['template', 'layout']:
        test = FunctionalDocTestSuite(dottedname % name)
        test.layer = TestLayer
        suite.addTest(test)

    test = FunctionalDocTestSuite(dottedname % 'directive')
    test.layer = TestMinimalLayer
    suite.addTest(test)

    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


