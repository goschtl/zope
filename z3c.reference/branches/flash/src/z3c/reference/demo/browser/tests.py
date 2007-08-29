__docformat__ = "reStructuredText"

import unittest
from zope.app.testing import functional
from zope.app.testing import setup
from z3c.configurator import configurator
from z3c.testing import layer

def appSetUp(app):
    configurator.configure(app, {},
                           names=["lovely.relation.o2oStringTypeRelations"])

layer.defineLayer('Z3cReferenceDemoLayer', zcml='ftesting.zcml',
                  appSetUp=appSetUp,
                  clean=True)

def test_suite():
    fsuites = (
        functional.FunctionalDocFileSuite('README.txt')
    )
    for fsuite in fsuites:
        fsuite.layer=Z3cReferenceDemoLayer
    return unittest.TestSuite(fsuites)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
