import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing import ZopeTestCase
ZopeTestCase.installProduct('Five')

from zope.app.tests.placelesssetup import setUp, tearDown

import Products.Five
from Products.Five import zcml
from zope.app import zapi
from zope.interface import Interface
from zope.app.component.interface import provideInterface
from Products.Five.utilities.interfaces import IMarkerUtility
from Products.Five.testing.interfaces import IStubInterface as IFace
from Products.Five.testing import manage_addFiveTraversableFolder

class Test(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        self.marker_util = zapi.getUtility(IMarkerUtility)
        self.iface_name ='.'.join((IFace.__module__, IFace.__name__))
        provideInterface(self.iface_name, IFace)
        manage_addFiveTraversableFolder(self.folder, 'test', "")
        self.test = self.folder.test

    def test_mark(self):
        self.marker_util.mark(self.test, IFace)
        self.assert_provided()
        
    def assert_provided(self):
        self.failUnless(self.iface_name in self.marker_util.getDirectlyProvidedNames(self.test))
        self.failUnless(IFace in self.marker_util.getDirectlyProvided(self.test))
        self.failIf(IFace in self.marker_util.getMarkerInterfaces(self.test))

    def assert_not_provided(self):
        self.failIf(self.iface_name in self.marker_util.getDirectlyProvidedNames(self.test))
        self.failIf(IFace in self.marker_util.getDirectlyProvided(self.test))
        
    def test_erase(self):
        self.test_mark()
        self.marker_util.erase(self.test, IFace)
        self.assert_not_provided()

    def test_update(self):
        # update is just a convenience method
        update = self.marker_util.update
        update(self.test, add=[IFace], remove=[IFace])
        self.assert_not_provided()
        update(self.test, add=[IFace])
        self.assert_provided()
        update(self.test, remove=[IFace])
        self.assert_not_provided()
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    return suite

if __name__ == '__main__':
    framework()
