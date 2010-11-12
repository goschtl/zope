import unittest
import doctest

from zope.app.wsgi.testlayer import BrowserLayer

from hurry.resource.wsgi import InjectMiddleWare
import hurry.zoperesource.tests


class HurryResourceBrowserLayer(BrowserLayer):
    def setup_middleware(self, app):
        return InjectMiddleWare(app)


def test_suite():
    suite = unittest.TestSuite()
    readme = doctest.DocFileSuite(
        '../README.txt',
        optionflags=doctest.NORMALIZE_WHITESPACE)
    readme.layer = HurryResourceBrowserLayer(hurry.zoperesource.tests)
    suite.addTest(readme)

    return suite
