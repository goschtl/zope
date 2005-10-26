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
from Products.Five.testing import manage_addFiveTraversableFolder

from Products.Five.traversable import FakeRequest
from Products.Five.utilities.browser.marker import EditView
from zope.app.apidoc.viewmodule.browser import ViewsDetails
from zope.app.traversing.browser.interfaces import IAbsoluteURL
from Products.Five.utilities.interfaces import IMarkerUtility
from zope.app.component.interface import provideInterface

def dummy(key):
    return key

_marker = object()

class Base(ZopeTestCase.ZopeTestCase):
    
    def beforeTearDown(self):
        tearDown()
        
    def afterSetUp(self):
        setUp()
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('permissions.zcml', Products.Five)
        zcml.load_config('configure.zcml', Products.Five.utilities)
        manage_addFiveTraversableFolder(self.folder, 'test_folder', "")
        self.test_folder = self.folder.test_folder
        uf = self.folder.acl_users
        uf._doAddUser('manager', 'r00t', ['Manager'], [])
        self.login('manager')

class Test(Base):
    """
    These are integration tests for making sure the component
    architecture and parts are working in a basic fashion
    """
    def afterSetUp(self):
        super(Test, self).afterSetUp()

    def test_viewsdetails(self):
        request = FakeRequest()
        self.marker_util = zapi.getUtility(IMarkerUtility)
        provideInterface(IAbsoluteURL.__name__, IAbsoluteURL)
        self.marker_util.mark(self.folder.test_folder, IAbsoluteURL)
        request['iface'] = request['all'] = request['type'] = IAbsoluteURL.__name__
        view = zapi.getView(self.folder.test_folder, 'views-details.html', request)
        assert view
        assert isinstance(view.getViewsByLayers(), list)
        try:
            view()
        except :
            import sys, pdb
            c, e, tb = sys.exc_info()
            pdb.post_mortem(tb)
        assert view() 
        
    def test_editview(self):
        request = FakeRequest()
        view = zapi.getView(self.folder.test_folder, 'edit-markers.html', request)
        assert view
        assert isinstance(view.getDirectlyProvidedNames(), list)
        assert isinstance(view.getProvidedNames(), list)
        try:
            view()
        except :
            import sys, pdb
            c, e, tb = sys.exc_info()
            pdb.post_mortem(tb)
        assert view() 

        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    return suite

if __name__ == '__main__':
    framework()
