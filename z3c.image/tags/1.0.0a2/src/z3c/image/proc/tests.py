import doctest
import unittest
from zope.testing.doctestunit import DocFileSuite, DocTestSuite
from zope.app.testing import functional
from zope import component
import adapter
from zope.app.file.interfaces import IImage
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


functional.defineLayer('Z3cImageLayer', 'ftesting.zcml')


def setUp(test):
    component.provideHandler(adapter.invalidateCache,
                             adapts=(IImage, IObjectModifiedEvent))

def tearDown(test):
    pass

def test_suite():
    ftests = functional.FunctionalDocFileSuite('BROWSER.txt')
    ftests.layer = Z3cImageLayer
    return unittest.TestSuite(
        (
        ftests,
        DocFileSuite('README.txt',
                     setUp=setUp,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocTestSuite('z3c.image.proc.browser',
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
