import doctest
import unittest
from zope.testing.doctestunit import DocFileSuite, DocFileSuite
from zope.app.testing import setup
import zope.traversing.testing
from zope.traversing.testing import browserView
from zope.traversing.browser import AbsoluteURL, SiteAbsoluteURL
from zope.traversing.interfaces import IContainmentRoot
from zope.traversing.browser.interfaces import IAbsoluteURL

def setUp(test):
    root = setup.placefulSetUp(True)
    zope.traversing.testing.setUp()
    test.globs['root'] = root

    browserView(None, 'absolute_url', AbsoluteURL)
    browserView(IContainmentRoot, 'absolute_url', SiteAbsoluteURL)
    browserView(None, '', AbsoluteURL, providing=IAbsoluteURL)
    browserView(IContainmentRoot, '', SiteAbsoluteURL, providing=IAbsoluteURL)

def tearDown(test):
    setup.placefulTearDown()

def test_suite():
    
    return unittest.TestSuite(
        (
        DocFileSuite('README.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
