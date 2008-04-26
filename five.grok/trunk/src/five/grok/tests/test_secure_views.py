import unittest
from Testing import ZopeTestCase
from test_all import setUp

from AccessControl import Unauthorized
from OFS.SimpleItem import SimpleItem

class TestViews(ZopeTestCase.ZopeTestCase):
    
    def afterSetUp(self):
        setUp()
        self.folder._setObject('item', SimpleItem())
        self.folder.item.id = 'item'
        
    def test_views(self):
        self.logout()
        self.assertRaises(Unauthorized, self.folder.item.restrictedTraverse, ('@@aview',))
        
    def test_views(self):
        self.logout()
        self.assertRaises(Unauthorized, self.folder.item.restrictedTraverse, ('@@aview',))
        
def test_suite():
    return unittest.makeSuite(TestViews)