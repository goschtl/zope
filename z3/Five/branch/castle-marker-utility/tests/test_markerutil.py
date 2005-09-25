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
from Products.Five.testing.interfaces import IStubInterface2, IStubInterface3
from Products.Five.testing import manage_addFiveTraversableFolder
from sets import Set

_marker = object()

def dotted(iface):
    return '.'.join((iface.__module__, iface.__name__))

ifaces = (IFace, IStubInterface2, IStubInterface3)
iface_names = tuple([dotted(x) for x in ifaces])

for iface_name, iface in zip(iface_names, ifaces):
    provideInterface(iface_name, iface)

class Test(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        self.marker_util = zapi.getUtility(IMarkerUtility)
        manage_addFiveTraversableFolder(self.folder, 'test_folder', "")
        self.test_folder = self.folder.test_folder
        self.iface, self.iface2, self.iface3 = iface_names
        self.orig_names = self.provided(self.test_folder)
        
    def provided(self, object):
        return self.marker_util.getDirectlyProvidedNames(self.test_folder)
    
    def test_mark(self):
        self.marker_util.mark(self.test_folder, IFace)
        self.assert_provided()
        self.check_conserve([self.iface] + self.orig_names)

    def check_conserve(self, original=_marker):
        provided = self.provided(self.test_folder)
        self.assertEqual(Set(provided), Set(original))
        
    def assert_provided(self):
        self.failUnless(self.iface in self.marker_util.getDirectlyProvidedNames(self.test_folder))
        self.failUnless(IFace in self.marker_util.getDirectlyProvided(self.test_folder))
        self.failIf(IFace in self.marker_util.getAvailableInterfaces(self.test_folder))

    def assert_not_provided(self):
        self.failIf(self.iface in self.marker_util.getDirectlyProvidedNames(self.test_folder))
        self.failIf(IFace in self.marker_util.getDirectlyProvided(self.test_folder))
        
    def test_erase(self):
        self.test_mark()
        self.marker_util.erase(self.test_folder, IFace)
        self.assert_not_provided()
        self.check_conserve(self.orig_names)

    def test_simpleupdate(self):
        # update is just a convenience method
        update = self.marker_util.update
        update(self.test_folder, add=[IFace], remove=[IFace])
        self.assert_not_provided()
        self.check_conserve(self.orig_names)

        update(self.test_folder, add=[IFace])
        self.assert_provided()
        self.check_conserve(self.orig_names + [self.iface])
        
        update(self.test_folder, remove=[IFace])
        self.assert_not_provided()
        self.check_conserve(self.orig_names)

    def test_conservancy(self):
        available = self.marker_util.getAvailableInterfaceNames(self.test_folder)
        provided = self.provided(self.test_folder)
        orig_markers = self.marker_util.getAvailableInterfaces(self.test_folder)
        self.marker_util.update(self.test_folder, add=orig_markers)
        self.assertEqual(Set(available), Set(self.provided(self.test_folder)) ^ Set(provided))
        self.marker_util.erase(self.test_folder, IStubInterface2)
        stub_tuple = (IStubInterface2,)
        self.assertEqual(self.marker_util.getAvailableInterfaces(self.test_folder), stub_tuple)
        self.assertEqual(Set(orig_markers) - Set(stub_tuple), Set(self.marker_util.getDirectlyProvided(self.test_folder)))
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    return suite

if __name__ == '__main__':
    framework()
