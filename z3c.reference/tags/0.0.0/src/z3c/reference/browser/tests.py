import doctest
import unittest
from zope.testing.doctestunit import DocFileSuite, DocTestSuite
from zope.app.testing import setup
from zope import component
from zope.dublincore.annotatableadapter import ZDCAnnotatableAdapter
from zope.dublincore.interfaces import IWriteZopeDublinCore
from zope.app.keyreference.testing import SimpleKeyReference
from zope.traversing.testing import browserView
from zope.traversing.browser.interfaces import IAbsoluteURL
from z3c.reference.interfaces import IViewReference
from zope.traversing.browser.absoluteurl import AbsoluteURL
from zope.publisher.browser import BrowserPage

from views import ViewReferenceAbsoluteURL

class TestPage(BrowserPage):

    def __call__(self):
        return "testpage"

def setUp(test):
    test.globs['site'] = setup.placefulSetUp(True)
    component.provideAdapter(SimpleKeyReference)
    component.provideAdapter(ZDCAnnotatableAdapter,
                             provides=IWriteZopeDublinCore)
    browserView(IViewReference, '', ViewReferenceAbsoluteURL,
                providing=IAbsoluteURL)
    browserView(None,'index.html',TestPage)

def tearDown(test):
    setup.placefulTearDown()


def test_suite():
    
    return unittest.TestSuite(
        (
        DocTestSuite('z3c.reference.browser.widget',
                     setUp=setUp,tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocTestSuite('z3c.reference.browser.views',
                     setUp=setUp,tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

