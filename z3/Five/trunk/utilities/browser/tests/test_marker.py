# this test will be converted to a doctest
import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest

from sets import Set
from zope.app import zapi

from Testing import ZopeTestCase

from zope.app.tests.placelesssetup import setUp, tearDown

import Products.Five
from Products.Five import zcml
from Products.Five.tests.testing import manage_addFiveTraversableFolder

from Products.Five.traversable import FakeRequest
from Products.Five.utilities.browser.marker import EditView
from zope.app.apidoc.viewmodule.browser import ViewsDetails

from zope.app.traversing.interfaces import IContainmentRoot
from Products.Five.utilities.interfaces import IMarkerUtility
from zope.app.component.interface import provideInterface

def dummy(key):
    return key

_marker = object()

class Base(ZopeTestCase.FunctionalTestCase):

    def beforeTearDown(self):
        tearDown()

    def afterSetUp(self):
        #setUp()
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.Five)
        zcml.load_config('permissions.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.Five.utilities)
        zcml.load_string('''<configure xmlns="http://namespaces.zope.org/zope"
                             xmlns:five="http://namespaces.zope.org/five">
                             <five:traversable class="OFS.Folder.Folder"/>
                             </configure>
                             ''')
        manage_addFiveTraversableFolder(self.folder, 'test_folder', "")
        self.test_folder = self.folder.test_folder
        uf = self.folder.acl_users
        uf._doAddUser('manager', 'r00t', ['Manager'], [])
        self.login('manager')

class TestKlasses(Base):

    def afterSetUp(self):
        super(Test, self).afterSetUp()

class Test(Base):
    """
    These are integration tests for making sure the component
    architecture and parts are working in a basic fashion
    """
    def afterSetUp(self):
        super(Test, self).afterSetUp()
        self.path = '/'.join(self.test_folder.getPhysicalPath())

    def test_viewsdetails(self):
        request = FakeRequest()
        iface = IContainmentRoot
        self.marker_util = zapi.getUtility(IMarkerUtility)
        provideInterface(iface.__name__, iface)
        self.marker_util.mark(self.folder.test_folder, iface)
        request['iface'] = request['all'] = request['type'] = iface.__name__
        view = zapi.getView(self.folder.test_folder, 'views-details.html', request)
        assert view
        assert isinstance(view.getViewsByLayers(), list)
##         resp = self.publish('%s/views-details.html?iface=%s' %(self.path, iface.__name__))
##         import pdb; pdb.set_trace()
##         print resp.getBody()

    def test_editview(self):
        request = FakeRequest()
        view = zapi.getView(self.folder.test_folder, 'edit-markers.html', request)
        assert view
        assert isinstance(view.getDirectlyProvidedNames(), list)
        assert isinstance(view.getProvidedNames(), list)
##         resp = self.publish('%s/edit-markers.html' %self.path)
##         import pdb; pdb.set_trace()
##         print resp.getBody()


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    return suite

if __name__ == '__main__':
    framework()
