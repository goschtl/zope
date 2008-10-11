import os

from Testing import ZopeTestCase

from zope.app.testing.functional import ZCMLLayer

zcmlPath = os.path.join(os.path.dirname(__file__), "tests.zcml")
testLayer = ZCMLLayer(zcmlPath, "five.clids",
                      'testLayer')


from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.publisher.browser import TestRequest

from plone.clids.interfaces import IHTML
from plone.clids.interfaces import IHTMLIdRegistry


class TestZodb(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        pass

    def testSomething(self):
        request = TestRequest()
        view = getMultiAdapter((self.folder, request), IHTML)
        htmlid = view.id
        self.assertEqual(htmlid, 'folder-/test_folder_1_')
        registry = getUtility(IHTMLIdRegistry)
        resolved = registry.getObject(htmlid, self.app)
        self.assertEqual(resolved, self.folder)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    test = makeSuite(TestZodb)
    test.layer = testLayer
    suite.addTest(test)
    return suite
