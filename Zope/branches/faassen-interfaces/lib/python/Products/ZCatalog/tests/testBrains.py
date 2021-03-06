##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Unittests for Catalog brains

$Id: testBrains.py,v 1.2 2004/03/23 21:27:03 caseman Exp $"""

import unittest
import Acquisition
from zExceptions import Unauthorized
from ZODB.POSException import ConflictError

class Happy(Acquisition.Implicit):
    """Happy content"""
    def __init__(self, id):
        self.id = id

class Secret(Happy):
    """Object that raises Unauthorized when accessed"""
    def __of__(self, parent):
        raise Unauthorized

class Conflicter(Happy):
    """Object that raises ConflictError when accessed"""
    def __of__(self, parent):
        raise ConflictError
        
class DummyRequest(Acquisition.Implicit):
    
    def physicalPathToURL(self, path, relative=False):
        if not relative:
            path = 'http://superbad.com' + path
        return path

_marker = object()
        
class DummyCatalog(Acquisition.Implicit):
    
    _objs = {'/happy':Happy('happy'), 
             '/secret':Secret('secret'), 
             '/conflicter':Conflicter('conflicter')}
    _paths = _objs.keys() + ['/zonked']
    _paths.sort()
    
    def restrictedTraverse(self, path, default=_marker):
        try:
            return self._objs[path].__of__(self)
        except (KeyError, Unauthorized):
            if default is not _marker:
                return default
            raise
    
    def getpath(self, rid):
        return self._paths[rid]
    
    def getobject(self, rid):
        return self.restrictedTraverse(self._paths[rid])

    def resolve_url(self, path, REQUEST):
        path =  path[path.find('/', path.find('//')+1):] # strip server part
        return self.restrictedTraverse(path)
        
class ConflictingCatalog(DummyCatalog):
    
    def getpath(self, rid):
        raise ConflictError

class TestBrains(unittest.TestCase):
    
    def setUp(self):
        self.cat = DummyCatalog()
        self.cat.REQUEST = DummyRequest()
    
    def makeBrain(self, rid):
        from Products.ZCatalog.CatalogBrains import AbstractCatalogBrain
        class Brain(AbstractCatalogBrain):
            __record_schema__ = {'test_field': 0, 'data_record_id_':1}
        return Brain(('test', rid)).__of__(self.cat)
    
    def testHasKey(self):
        b = self.makeBrain(1)
        self.failUnless(b.has_key('test_field'))
        self.failUnless(b.has_key('data_record_id_'))
        self.failIf(b.has_key('godel'))
    
    def testGetPath(self):
        b = [self.makeBrain(rid) for rid in range(3)]
        self.assertEqual(b[0].getPath(), '/conflicter')
        self.assertEqual(b[1].getPath(), '/happy')
        self.assertEqual(b[2].getPath(), '/secret')
    
    def testGetPathPropagatesConflictErrors(self):
        self.cat = ConflictingCatalog()
        b = self.makeBrain(0)
        self.assertRaises(ConflictError, b.getPath)
        
    def testGetURL(self):
        b = self.makeBrain(0)
        self.assertEqual(b.getURL(), 'http://superbad.com/conflicter')
    
    def testGetRID(self):
        b = self.makeBrain(42)
        self.assertEqual(b.getRID(), 42)
    
    def testGetObjectHappy(self):
        b = self.makeBrain(1)
        self.assertEqual(b.getPath(), '/happy')
        self.failUnless(b.getObject().aq_base is self.cat.getobject(1).aq_base)
    
    def testGetObjectPropagatesConflictErrors(self):
        b = self.makeBrain(0)
        self.assertEqual(b.getPath(), '/conflicter')
        self.assertRaises(ConflictError, b.getObject)
    
    def testGetObjectReturnsNoneForUnauthorized(self):
        b = self.makeBrain(2)
        self.assertEqual(b.getPath(), '/secret')
        self.assertEqual(b.getObject(), None)
    
    def testGetObjectReturnsNoneForMissing(self):
        b = self.makeBrain(3)
        self.assertEqual(b.getPath(), '/zonked')
        self.assertRaises(KeyError, self.cat.getobject, 3)
        self.assertEqual(b.getObject(), None)        

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestBrains))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
