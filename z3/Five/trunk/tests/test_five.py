import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# XXX hack but no other way to initialize options apparently
from Zope.Startup.run import configure
configure('../../../etc/zope.conf')

from Testing import ZopeTestCase

ZopeTestCase.installProduct('Five')
ZopeTestCase.installProduct('FiveTest')

from zope.component import getAdapter
from Products.FiveTest.classes import Adaptable
from Products.FiveTest.interfaces import IAdapted

class FiveTestCase(ZopeTestCase.ZopeTestCase):
    def beforeSetUp(self):
        self.root = self._app()

    def test_adapters(self):
        obj = Adaptable()
        adapted = getAdapter(obj, IAdapted)
        self.assertEquals(
            "Adapted: The method",
            adapted.adaptedMethod())

    def test_adapters2(self):
        obj = Adaptable()
        adapted = IAdapted(obj)
        self.assertEquals(
            "Adapted: The method",
            adapted.adaptedMethod())
        
    
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(FiveTestCase))
        return suite
