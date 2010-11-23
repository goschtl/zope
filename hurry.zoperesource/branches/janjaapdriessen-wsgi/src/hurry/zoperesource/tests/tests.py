import unittest
import doctest

from zope.interface import Interface
from zope.component import getGlobalSiteManager
from zope.app.wsgi.testlayer import BrowserLayer
from zope.publisher.interfaces.browser import IBrowserRequest

from hurry.resource.wsgi import InjectMiddleWare
from hurry.zoperesource.zcml import create_resource_factory
from hurry.zoperesource.tests.view import foo
import hurry.zoperesource.tests

class HurryResourceBrowserLayer(BrowserLayer):

    def testSetUp(self):
        super(HurryResourceBrowserLayer, self).testSetUp()

        # Because it is difficult to dynamically register a entry_point in
        # tests, we do the setup by hand:
        resource_factory = create_resource_factory(foo)
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(
            resource_factory, (IBrowserRequest,), Interface, foo.name)

    def setup_middleware(self, app):
        return InjectMiddleWare(app)

def test_suite():
    readme = doctest.DocFileSuite(
        '../README.txt',
        optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS)
    readme.layer = HurryResourceBrowserLayer(hurry.zoperesource.tests)
    return unittest.TestSuite([readme])
