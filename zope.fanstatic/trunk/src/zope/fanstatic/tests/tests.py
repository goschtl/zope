import unittest
import doctest

from zope.interface import Interface
from zope.component import getGlobalSiteManager
from zope.app.wsgi.testlayer import BrowserLayer
from zope.publisher.interfaces.browser import IBrowserRequest

from fanstatic import InjectMiddleware

from zope.fanstatic.zcml import create_factory
from zope.fanstatic.tests.view import foo
import zope.fanstatic.tests

class ZopeFanstaticBrowserLayer(BrowserLayer):

    def testSetUp(self):
        super(ZopeFanstaticBrowserLayer, self).testSetUp()
        # Because it is difficult to dynamically register a
        # entry_point in tests, we do the setup by hand:
        resource_factory = create_factory(foo)
        getGlobalSiteManager().registerAdapter(
            resource_factory, (IBrowserRequest,), Interface, foo.name)

    def setup_middleware(self, app):
        return InjectMiddleware(app)

def test_suite():
    readme = doctest.DocFileSuite(
        '../README.txt',
        optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS)
    readme.layer = ZopeFanstaticBrowserLayer(zope.fanstatic.tests)
    return unittest.TestSuite([readme])
